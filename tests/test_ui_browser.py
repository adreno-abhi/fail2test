"""Real Chromium acceptance tests; install the optional browser dependency group first."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from test_ui_server import ui_server  # noqa: F401

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect
ARTIFACTS = Path(__file__).resolve().parents[1] / "output/playwright"


@pytest.fixture
def page(ui_server):  # noqa: F811
    with playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        current = context.new_page()
        errors = []
        external = []
        current.on("pageerror", lambda error: errors.append(str(error)))
        current.on(
            "request",
            lambda req: (
                external.append(req.url) if not req.url.startswith(ui_server.origin + "/") else None
            ),
        )
        current.goto(f"{ui_server.origin}/#session={ui_server.token}")
        expect(current.get_by_role("heading", name=ui_server.workspace.root.name)).to_be_attached()
        yield current
        assert not errors, errors
        assert not external, external
        context.close()
        browser.close()


def sample(page):
    page.get_by_role("button", name="Import failure.json", exact=True).click()
    expect(page.locator("#case-workspace")).to_be_visible()
    expect(page.locator("#case-state")).to_have_text("Review required")


@pytest.mark.parametrize("from_dialog", [False, True])
def test_first_use_demo_requires_no_upload(page, from_dialog):
    if from_dialog:
        page.get_by_role("button", name="+ Import evidence", exact=True).click()
        page.get_by_text("What file should I upload?", exact=True).click()
        expect(page.get_by_role("dialog")).to_contain_text("Screenshots, plain error logs")
        expect(page.get_by_role("dialog")).to_contain_text("does not connect Fail2Test")
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(ARTIFACTS / "import-guidance-desktop.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(ARTIFACTS / "import-guidance-mobile.png"), full_page=True)
        page.get_by_role("button", name="Try included example instead (no upload)").click()
        expect(page.get_by_role("dialog")).not_to_be_visible()
    else:
        page.get_by_role("button", name="Try included example (no upload)", exact=True).click()
    expect(page.locator("#case-workspace")).to_be_visible()
    expect(page.locator("#case-title")).to_contain_text("refund")
    expect(page.locator("#case-state")).to_have_text("Review required")


def test_first_use_without_sample_explains_setup(page, ui_server):  # noqa: F811
    (ui_server.workspace.root / "failure.json").unlink()
    page.reload()
    expect(page.locator("#sample-setup")).to_be_visible()
    expect(page.locator("#sample-setup")).to_contain_text("fail2test init demo")
    expect(page.locator("#welcome-sample")).to_be_hidden()
    page.get_by_role("button", name="+ Import evidence", exact=True).click()
    expect(page.locator("#import-sample")).to_be_hidden()
    expect(page.get_by_label("JSON file (maximum 10 MiB)")).to_be_visible()


def approve(page):
    page.get_by_role("tab", name="02 Review").click()
    page.get_by_label("Reviewer label").fill("acceptance-owner")
    page.get_by_label("I reviewed the recorded evidence", exact=False).check()
    page.get_by_role("button", name="Approve exact case").click()
    expect(page.locator("#case-state")).to_have_text("Reviewed")
    expect(page.locator("#panel-execution")).to_be_visible()


def validate(page):
    page.get_by_role("button", name="Validate failing baseline").click()
    expect(page.get_by_role("heading", name="Baseline reproduced", exact=False)).to_be_visible(
        timeout=20000
    )
    expect(page.locator("#case-state")).to_have_text("Baseline reproduced")


def test_browser_failure_to_fixed_pytest_export(page, ui_server):  # noqa: F811
    sample(page)
    approve(page)
    page.get_by_role("tab", name="05 Export").click()
    expect(page.locator("#export-help")).to_contain_text("Validate failing baseline")
    expect(page.get_by_role("button", name="Save export", exact=True)).to_be_disabled()
    page.get_by_role("tab", name="03 Execute").click()
    validate(page)
    page.get_by_role("button", name="Run regression", exact=True).click()
    expect(page.get_by_role("heading", name="Regression failed", exact=False)).to_be_visible(
        timeout=20000
    )
    page.get_by_label("Configured runner").select_option("fixed")
    page.get_by_role("button", name="Run regression", exact=True).click()
    expect(page.get_by_role("heading", name="Regression passed", exact=False)).to_be_visible(
        timeout=20000
    )
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(ARTIFACTS / "execution-desktop.png"), full_page=True)
    page.get_by_role("tab", name="05 Export").click()
    expect(page.locator("#export-help")).to_contain_text("Preview files")
    expect(page.get_by_role("button", name="Save export", exact=True)).to_be_disabled()
    page.get_by_role("button", name="Preview files").click()
    expect(page.locator("#export-help")).to_contain_text("Save export is now enabled")
    expect(page.get_by_text("Preview only · exports/regression", exact=True)).to_be_visible()
    assert not (ui_server.workspace.root / "exports/regression").exists()
    expect(page.locator("#export-result")).to_contain_text("runner='fixed'")
    page.get_by_role("button", name="Save export", exact=True).click()
    expect(page.get_by_text("Saved: exports/regression", exact=True)).to_be_visible()
    expect(page.locator("#export-help")).to_contain_text("Export saved")
    assert (ui_server.workspace.root / "exports/regression/test_regression.py").is_file()
    assert page.evaluate("location.hash") == ""


def test_browser_invalid_rules_edits_and_export_guard(page):
    sample(page)
    page.get_by_role("tab", name="05 Export").click()
    page.get_by_role("button", name="Preview files").click()
    expect(page.get_by_role("alert").first).to_contain_text("REVIEW_REQUIRED")
    approve(page)
    page.get_by_role("tab", name="02 Review").click()
    rule = page.get_by_label("Rule 1 JSON", exact=True)
    original = rule.input_value()
    rule.fill('{"id":"bad","kind":"output"}')
    page.get_by_role("button", name="Save case edits").click()
    expect(page.get_by_role("alert").first).to_contain_text("INVALID_DATA")
    expect(page.locator("#case-state")).to_have_text("Reviewed")
    changed = json.loads(original)
    changed["requirement"] = "Keep this behavior stable after fixes."
    rule.fill(json.dumps(changed))
    page.get_by_role("button", name="Save case edits").click()
    expect(page.locator("#case-state")).to_have_text("Review required")
    page.get_by_role("tab", name="03 Execute").click()
    page.get_by_role("button", name="Run regression", exact=True).click()
    expect(page.get_by_role("alert").first).to_contain_text("REVIEW_REQUIRED")


def test_browser_reduction_requires_review(page):
    sample(page)
    approve(page)
    validate(page)
    page.get_by_role("tab", name="04 Reduce").click()
    page.get_by_label("Maximum attempts", exact=False).fill("3")
    page.get_by_role("button", name="Reduce failing input").click()
    expect(page.get_by_role("heading", name="Derived case needs a new review")).to_be_visible(
        timeout=30000
    )
    expect(page.get_by_text("Original input", exact=True)).to_be_visible()
    expect(page.get_by_text("Reduced input", exact=True)).to_be_visible()
    page.get_by_role("button", name="Open derived case for review").click()
    expect(page.locator("#case-state")).to_have_text("Review required")
    expect(page.locator("#panel-review")).to_be_visible()


def test_browser_all_rule_templates_and_unapproved_proposals(page):
    sample(page)
    page.get_by_role("tab", name="02 Review").click()
    page.get_by_role("button", name="Suggest rules", exact=False).click()
    expect(page.locator("#draft-state")).to_contain_text("Unsaved changes")
    expect(page.locator("#case-state")).to_have_text("Review required")
    page.get_by_role("button", name="Save case edits").click()
    expect(page.locator("#draft-state")).to_have_text("No unsaved changes.")
    for kind in ("tool_argument", "forbidden_tool", "output", "max_tool_calls"):
        page.get_by_label("Add a rule", exact=True).select_option(kind)
        page.get_by_role("button", name="Add template", exact=True).click()
    expect(page.locator("#rule-editors textarea")).to_have_count(5)
    page.get_by_role("button", name="Save case edits").click()
    expect(page.locator("#draft-state")).to_have_text("No unsaved changes.")
    expect(page.locator("#selected-rule option")).to_have_count(5)
    page.locator("#case-json").evaluate("element => element.closest('details').open = true")
    source = page.get_by_label("Case JSON", exact=True).input_value()
    page.get_by_label("Case JSON", exact=True).fill(
        source.replace(
            '"schema_version": "0.1"', '"schema_version": "0.1", "schema_version": "0.1"'
        )
    )
    page.get_by_role("button", name="Apply JSON to draft").click()
    page.get_by_role("button", name="Save case edits").click()
    expect(page.get_by_role("alert").first).to_contain_text("DUPLICATE_JSON_KEY")


def test_browser_ai_preview_send_apply_requires_new_review(page, case_data, monkeypatch):

    calls = []
    monkeypatch.setenv("OPENROUTER_API_KEY", "synthetic-browser-test-key")

    def fake_provider(url, body, key, timeout):
        calls.append(body)
        rule = dict(case_data["rules"][0], id="ai-call-limit")
        return {
            "model": "test-free-model",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": json.dumps({"rules": [rule], "notes": ["Review intent."]})
                    },
                }
            ],
        }

    monkeypatch.setattr("fail2test.suggestions.send_http", fake_provider)
    sample(page)
    page.get_by_role("tab", name="02 Review").click()
    page.get_by_text("Optional AI-assisted suggestions", exact=True).click()
    page.get_by_label("Intended behavior for AI suggestions").fill("At most one refund per order.")
    page.get_by_role("button", name="Preview AI request", exact=True).click()
    expect(page.locator("#ai-preview-content")).to_contain_text("Free-only profile")
    assert not calls
    expect(page.get_by_role("button", name="Send previewed AI request")).to_be_disabled()
    page.get_by_label("I reviewed this payload", exact=False).check()
    page.get_by_role("button", name="Send previewed AI request").click()
    expect(page.get_by_role("button", name="Apply suggestions to draft")).to_be_visible(
        timeout=10000
    )
    assert len(calls) == 1 and calls[0]["provider"]["max_price"]["prompt"] == 0
    expect(page.locator("#case-state")).to_have_text("Review required")
    page.get_by_role("button", name="Apply suggestions to draft").click()
    assert "ai-call-limit" in page.get_by_label("Rule 1 JSON", exact=True).input_value()
    expect(page.locator("#draft-state")).to_contain_text("Unsaved changes")
    page.get_by_role("button", name="Save case edits").click()
    expect(page.locator("#selected-rule")).to_contain_text("ai-call-limit")
    expect(page.locator("#case-state")).to_have_text("Review required")
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(ARTIFACTS / "ai-suggestions-desktop.png"), full_page=True)


def test_browser_upload_xss_keyboard_responsive_and_missing_evidence(page, case_data):
    page.get_by_role("button", name="+ Import evidence", exact=True).click()
    expect(
        page.get_by_role("dialog").get_by_label("New case bundle name", exact=True)
    ).to_be_focused()
    page.get_by_label("Or paste JSON evidence").fill("{}")
    page.get_by_role("button", name="Sanitize and import").click()
    expect(page.locator("#import-error")).to_contain_text("UNSUPPORTED_FORMAT")
    case_data["title"] = '<img src="https://example.invalid/x" onerror="window.XSS=true">'
    case_data["input"]["password"] = "must-not-persist-browser-secret"
    case_data["model_fixtures"] = []
    page.get_by_label("JSON file (maximum 10 MiB)").set_input_files(
        {
            "name": "evidence.json",
            "mimeType": "application/json",
            "buffer": json.dumps(case_data).encode(),
        }
    )
    expect(page.get_by_label("Or paste JSON evidence")).not_to_have_value("{}")
    page.get_by_role("button", name="Sanitize and import").click()
    expect(page.locator("#case-title")).to_have_text(case_data["title"])
    assert page.evaluate("window.XSS === undefined")
    assert page.locator("#case-title img").count() == 0
    approve(page)
    page.get_by_role("button", name="Run regression", exact=True).click()
    expect(page.get_by_role("heading", name="Incomplete execution", exact=False)).to_be_visible(
        timeout=20000
    )
    first = page.get_by_role("tab", name="01 Evidence")
    first.focus()
    first.press("ArrowRight")
    expect(page.get_by_role("tab", name="02 Review")).to_be_focused()
    expect(page.locator("#panel-review")).to_be_visible()
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(ARTIFACTS / "review-mobile.png"), full_page=True)
