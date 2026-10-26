# Local UI verification

26 October 2026. Implemented under the owner's approval for the local UI step.
The next feature and GitHub publication still require separate approval.

## Delivered behavior

- `fail2test ui`: explicitly started loopback server against an existing workspace/config.
- Bundled, formatted HTML/CSS/JavaScript with no frontend build or Node requirement for users.
- Supported file/paste/sample import, in-memory sanitization, evidence/fixture inspection,
  completeness/provenance report, deterministic proposals and all five rule templates.
- JSON rule/case editing, schema diagnostics, explicit acknowledgement/reviewer/selected rule,
  digest checks and clearing review/baseline after saving edits.
- Actual background run/validate/reduction jobs, one at a time, using the existing engine.
  Review editing is disabled while jobs run. Results distinguish failed behavior from incomplete
  execution and baseline reproduction from regression success.
- Original/reduced input comparison, derived-case review, shared engine export preview and
  explicit save into new workspace directories. Preview imports no application code.
- Exact Host, bearer session and same-origin mutation checks; no CORS, restrictive CSP,
  inert text rendering, bounded JSON/requests, static route allowlist, path/link containment.
- Browser walkthrough and installed wheel/source asset/API smoke checks.

## Verification evidence

The UI-specific tests exercise real HTTP requests and headless Chromium, rather than mocked
screens. They cover the complete key-free broken/fixed workflow, invalid edits, missing model
fixtures, unapproved proposals, all rule templates, reduction requiring review, export guards,
duplicate JSON keys, script-like evidence, keyboard tabs, dialog focus and a 390-pixel viewport.
HTTP checks additionally reject wrong/missing session/origin, hostile Host, path traversal and
symlink escapes, unknown executable runner selection, excess bodies and stale mutations.
They verify sanitized persisted uploads, inert inspection, serialized jobs, timeouts and engine
export parity. CLI launch/open/no-open/shutdown paths have direct tests.

Screenshots were visually reviewed: `output/playwright/execution-desktop.png` (1440px) and
`output/playwright/review-mobile.png` (390px). They are ignored local artifacts and contain only
synthetic examples. Browser network checks permit only the actual loopback origin.

| Final check | Actual result |
|---|---|
| Full suite with subprocess coverage and browser group | **148 passed**, 88% combined statement/branch coverage |
| UI-specific HTTP/browser suite | 28 passing cases in the final full run, including 5 Chromium tests |
| Ruff lint / formatting | PASS; 80 Python files formatted |
| mypy | PASS; 19 source files |
| Strict MkDocs build | PASS |
| Locked dependency resolution | PASS |
| Wheel / source-distribution build | PASS |
| Fresh core wheel workflow plus installed UI assets/API | PASS |
| Fresh source install plus installed UI assets/API | PASS |
| Fresh optional native LangGraph workflow | PASS |
| Git whitespace check | PASS |

Full-suite command: `uv run --group browser pytest --cov=fail2test --cov-report=term -q`.
Package command: `uv build`, followed by `uv run python scripts/smoke_package.py`.
UI smoke runs using the isolated environment's Python, outside the checkout, without Node,
Playwright or the optional framework installed. Development Chromium is not a runtime dependency.

## Environment and limits

Windows, CPython 3.13.5, Playwright 1.64.1 with its Chromium, native dependencies from uv.lock.
Clean core installation does not include Playwright or LangGraph; it serves packaged assets
and the authenticated API using Python alone. Native smoke verification remains separate.
No model provider, real payment call, account, deployment or publishing action is involved.

This is functional/keyboard/responsive verification, not a formal accessibility audit or a
security certification. Other browsers/OS/Python combinations remain unverified in this step.
The server is for local trusted workspaces only, not internet hosting or hostile-code isolation.
Configured Python remains executable trusted code. External editors are not locked by the UI.
Jobs have bounded runtime but no cancel button. In-memory job history is session-local.
Reduction deletes input values only; optional AI proposals remain unimplemented.

## Implementation references

The [build contract](../planning/LOCAL_UI_BUILD.md) defines ownership and boundaries; the
[walkthrough](../site/local-ui.md) defines the usable workflow. Server design accounts for
Python's [HTTP server limitations](https://docs.python.org/3/library/http.server.html) and
uses explicit Origin/token checks consistent with the
[OWASP CSRF guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).
Browser checks use the official [Playwright Python API](https://playwright.dev/python/docs/intro).
