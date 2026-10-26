# Local browser workflow

The UI uses the same review, execution, reduction and export engine as the CLI.
It needs no Node.js, account, database or model key.

## Start with the example

```text
uv sync --locked --all-extras
uv run fail2test init local-artifacts/ui-demo
uv run fail2test ui --workspace local-artifacts/ui-demo
```

For an installed package, use `fail2test` directly. The command opens your default browser.
Use `--no-open` to open the printed launch URL yourself. `--port 0` selects an available
port; the default is 8765. The server binds only `127.0.0.1`.

Keep the terminal open. The launch URL contains an ephemeral token in its fragment;
the UI stores it in that browser tab and removes it from the address bar. Treat the URL
as private. Restarting invalidates old tokens. For SESSION_REQUIRED, reopen the new full
launch URL from the terminal.

For an existing application, choose its workspace and existing trusted configuration:

```text
fail2test ui --workspace path/to/application --config testing/fail2test.toml
```

The config path is relative to the workspace. Registered runners appear in Execute.
The browser cannot edit configuration or register imports. Invalid/missing configuration
prevents startup; follow the [integration guide](integration.md) first.

## Complete the workflow

### What counts as evidence?

For the tutorial, **Try included example (no upload)** on the welcome screen, or
**Try included example instead (no upload)** in the import dialog, loads the workspace's
`failure.json`. It contains a synthetic agent plan requesting two refunds, the recorded
refund response and a rule requiring one refund. Nothing is charged or sent to a model.
These buttons appear in a workspace created by `fail2test init`; if there is no sample,
the welcome screen explains how to create a separate demo workspace.

For your own failure, upload a **Fail2Test case v0.1** (`input`, `model_fixtures`,
`tool_fixtures`, `rules`, identity and provenance fields), or a **neutral trace v0.1**
containing input, completeness and paired model/tool request/result events. In the source
repository, the case example is `src/fail2test/data/duplicate-refund.case.json` and the
neutral trace schema is `docs/planning/reference/trace.schema.json`.
The UI accepts the same formats as CLI `import`. Ordinary log text, screenshots, ZIPs
and arbitrary vendor exports need conversion first; there is no automatic trace collector.
Review/remove private data before importing.

The recording supplies dependency responses; your configured application-owned runner
executes current code against them. Importing a file alone does not integrate an application;
follow the [integration guide](integration.md). Missing recorded interactions cannot prove
a regression or a fix. Neutral imports also need you to add and review behavioral rules.

### Import, review and execute

1. Click **Import failure.json** to import the initialized example into a new `cases/`
   bundle. **Import evidence** accepts a supported JSON file or pasted evidence and a new
   bundle name. Importing/inspecting does not execute application code.
2. In **Evidence**, inspect input, model/tool fixtures, completeness, provenance and the
   sanitization report. Original events appear only for imported neutral traces.
3. In **Review**, inspect the assertions. Templates cover all five rule kinds with editable
   JSON forms. **Suggest rules** provides deterministic, unapproved hypotheses. Use advanced
   JSON for input/fixture changes: apply to draft, then **Save case edits**. Save validates
   the schema and clears prior review/baseline. At least one valid rule is required.
4. Enter a reviewer label, choose the known failing assertion, acknowledge the evidence and
   rules, then **Approve exact case**. This approval binds the saved content digest.
5. In **Execute**, select `broken`, then **Validate failing baseline**. The selected assertion
   must fail in a complete run. **Run regression** with `broken` shows failure; with `fixed`
   it passes. In your project, make the application fix in your usual editor and run again.
6. Optionally select `broken` again and **Reduce**. Choose a new case name and attempt
   budget. Compare inputs and the report; open the derived case for renewed review and
   baseline validation. Reduction only deletes input values and preserves the selected failure.
7. Select `fixed` in Execute, open **Export**, choose a new name, **Preview files**, inspect
   the test/bundle and **Save export**. Preview writes nothing. Outputs go into `exports/NAME/`.

```text
uv run pytest local-artifacts/ui-demo/exports/regression/test_regression.py -q
```

The export runner must satisfy assertions for pytest to pass. A reproduced baseline alone
does not prove that runner passes. Fixture tests check handling of recorded responses;
they do not evaluate changed prompts against live models.

## Errors and limits

Optional provider/model selection lives under **Review → Optional AI-assisted suggestions**.
See [AI suggestions](ai-suggestions.md) for configuration, payload preview, explicit consent
and credential handling. The deterministic suggestion button remains key-free.

- **Review required / stale case:** reopen an externally edited bundle and review again.
  Save browser edits before running. Invalid edits preserve saved content. Case-list refresh
  does not discard drafts. Reopening a bundle clears prior session reports from the view.
- **Trace only:** incomplete source evidence cannot establish a current-code regression.
- **Baseline not reproduced:** inspect the selected assertion and runner. A complete pass
  is not a reproduced failure. Missing/unsupported fixtures produce incomplete results.
- **Save export disabled:** read the guidance beside the export controls. For the demo,
  select `broken` in Execute and **Validate failing baseline**, then select `fixed` and
  **Run regression**. In Export, click **Preview files** and inspect them before **Save
  export** becomes enabled. Running a regression alone does not establish the baseline;
  saving edits or approving again clears it. Changing export settings requires a new preview.
- **Workspace busy:** one job runs at a time. Run/validate workers are capped at 30 seconds;
  reduction has a 30-second total budget. There is no cancellation button. Ctrl+C stops the
  server after bounded in-flight work finishes.
- **Output exists:** choose a new name. Existing exports/derived bundles are never overwritten.
- **Unsafe path:** paths stay within the workspace. Links/junctions, hidden components,
  parent/absolute/drive paths are rejected. Listing is capped at 200 bundles / 2,000 visited
  directories, excluding hidden directories and dependency caches. Choose a parent workspace
  for bundles; a bundle directly at the workspace root is not listed.
- JSON documents and the surrounding HTTP request are capped at 10 MiB. Heavily escaped
  source JSON may need a smaller upload to fit the request envelope.

Known sensitive values are sanitized in memory before upload persistence. Detection is best
effort; inspect saved artifacts before sharing. Original source files remain unchanged.
Evidence renders as text; its URLs are not fetched. The last 20 execution jobs are held in
memory for this session. Bundles and exports persist on disk.

The API requires a bearer session token, exact local Host and same-origin mutations. There
is no CORS access. Only bundled static assets are served. Do not expose the server through
a proxy/tunnel. Trusted Python/application code can access local resources; supervision is
not a sandbox. Unrelated local editors/processes are outside the UI's lock.

## Browser checks for contributors

```text
uv sync --locked --all-extras --group browser
uv run --group browser playwright install chromium
uv run --group browser pytest tests/test_ui_browser.py -q
```

Browser dependencies are development-only. Screenshots go into ignored `output/playwright/`.
HTTP tests run in the normal suite. Assets are packaged source; no frontend build is needed.
Optional formatting: `npx --yes prettier@3.6.2 --write src/fail2test/ui/static/`.
