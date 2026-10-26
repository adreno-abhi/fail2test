# Local UI build contract

26 October 2026. Owner approval: latest “go ahead”, bounded by LOCAL_UI_SCOPE.md.
This is implementation clearance for the local UI only; publication remains unapproved.

## Stage 1 — direction: PASS

EXISTS: approved scope, Case/Manifest contracts, CLI workflow and supervised execution.
Browser → authenticated loopback HTTP API → existing engine → workspace bundles.
The filesystem is the source of truth; the browser holds only unsaved edits and display state.
The Python package owns the server and bundled native HTML/CSS/JavaScript. No frontend
runtime dependency, accounts, provider calls or internet assets. Only the owner-selected
TOML configuration may select executable application code. Imported cases remain data.

## Stage 2 — build contract: PASS

`ui --workspace PATH --config RELATIVE_PATH --port PORT --no-open` binds 127.0.0.1.
GET workspace/cases/case/jobs provides bounded data; POST import/edit/propose/review/jobs/
export-preview/export provides explicit actions. Bodies are bounded JSON, duplicate keys
are rejected, and uploads are sanitized in memory before persistence. APIs require a
random session bearer token; POST also requires the exact local Origin. Exact Host
validation, no CORS, restrictive CSP and a static route allowlist enforce the browser boundary.
Tokens enter the browser through a URL fragment and are removed from the address bar.

Workspace-relative paths reject traversal, hidden paths, drive/UNC paths and symlink escapes.
Browser writes are restricted to case bundle data and new export/reduction directories.
Mutations check the expected digest; edits clear review/baseline. One bounded background
job runs at a time; other mutations fail WORKSPACE_BUSY. Run/validate workers are capped
at 30 seconds; reduction has a 30-second total budget. Job status reflects real completion,
not simulated progress. There is no cancellation button; shutdown waits for bounded work.
Preview and export share engine preparation and baseline checks, with no application import.
Errors return stable codes and safe messages; raw exceptions and request logs are suppressed.

Evidence, review, execution, reduction and export share one accessible case workspace.
Imported content uses text nodes. Unsaved edits block execution. Typed rule templates and
JSON editing support all five rule kinds. Explicit reviewer acknowledgement selects the
failure to reproduce. Derived cases need review again. No synthetic event timeline.

Acceptance evidence: HTTP adversarial tests, browser workflow and responsive/keyboard
checks, existing CLI parity, installed-wheel asset smoke check. Tests must distinguish
historical evidence from fresh execution and incomplete execution from behavioral failure.

## Stage 3 — local run guidance: PASS

Only local operation is in scope. Use an existing workspace/config or `fail2test init`.
No database, migration, cloud identity or persistent credential is needed. Session tokens
are ephemeral; restart rotates them. Ctrl+C closes the server after bounded execution.
Rollback is stopping the UI; portable case files and CLI remain usable. Back up/version
workspace files normally. No HTTP access/body logs are retained; current job status is in
memory. Browser tests and wheel smoke checks verify setup before step completion.

Known boundary: trusted local processes and configured Python code can access local files;
this server and its worker supervision are not a sandbox. Do not expose it through a proxy
or network tunnel. Concurrent external filesystem edits are detected at action boundaries,
but the UI cannot serialize unrelated editors. Production internet hosting is out of scope.

Owner: project maintainer. Implementation/testing: current Codex task. Final acceptance:
project owner at the end of this step. Browser/package evidence is PARTIAL until checks run;
these gate decisions establish a buildable contract, not a completed-release claim.
