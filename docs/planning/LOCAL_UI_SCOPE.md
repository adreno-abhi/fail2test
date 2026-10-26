# Local browser UI — approved product scope

The project owner approved including a focused local UI in the first complete public release on 26 October 2026 and subsequently approved its implementation. The bundled UI is now implemented; see the [browser walkthrough](../site/local-ui.md) and [verification record](../development/local-ui-verification.md).

## Purpose

Help developers understand recorded evidence, review intended behavior and produce a useful regression without requiring them to learn every CLI option first. The CLI, Python interface, pytest output and existing CI integration remain first-class workflows.

The UI uses the existing case, review, execution, reduction and export engine. It must not maintain a competing assertion evaluator or report an outcome differently from the CLI.

## Proposed user flow

1. Start the UI explicitly against a chosen local workspace. A proposed `fail2test ui` command will be finalized during implementation.
2. Import supported evidence or open a local case bundle. Show completeness and the distinction between historical evidence and fresh execution.
3. Inspect recorded interactions/fixtures, sanitization changes and candidate assertions. Show a timeline only when the source actually contains suitable events.
4. Edit supported rules, inspect affected values and acknowledge review. Editing case content invalidates prior review/validation exactly as it does in the CLI.
5. Choose an already configured trusted runner and explicitly start validation/regression execution. Show complete/pass, complete/fail and incomplete/error distinctly.
6. Compare original and reduced inputs with the selected failure and reduction budget/results. Derived cases require renewed review.
7. Preview the generated pytest test and portable files, then explicitly export to a selected location in the workspace.

## Focused screens

| View | Primary job |
|---|---|
| Workspace / cases | Open/import a case and see its lifecycle/completeness |
| Evidence inspector | Read recorded messages, tool interactions and fixture requirements |
| Review | Inspect sanitization changes, edit typed rules and acknowledge the exact digest |
| Execution results | Choose a configured runner, run explicitly and explain failures/incomplete results |
| Reduction comparison | Show input changes and evidence that the selected failure was retained |
| Export preview | Inspect the test/fixtures and save portable outputs |

These views may share a single case workspace with tabs rather than requiring separate pages. Final layout and frontend stack belong to the approved UI implementation step. Avoid ornamental charts, invented activity metrics, fake execution progress and empty commercial features.

## Local operation and packaging

- No account or hosted service is required. The browser connects to an explicitly started local server, bound to loopback by default.
- The UI is optional to launch; CLI/library users need no running web server.
- Bundle frontend assets with the Python distribution. End users should not need Node.js, a frontend build or external CDNs/fonts/analytics.
- Use the same versioned contracts and error codes as the engine. The server is a thin orchestration layer; it does not duplicate business rules.
- Explain that the selected application's runner is trusted executable code. A local UI does not turn the existing subprocess into a hostile-code sandbox.
- Deterministic suggestions and fixture execution work without model credentials. AI-assisted suggestions remain a separate, unimplemented feature.

## Required controls

The concrete implementation must define and test local-server request/origin protections, per-session authorization, workspace path containment and explicit execution actions. An unrelated website must not be able to trigger the local runner through cross-origin requests. There is no need for user-account infrastructure to provide those local protections.

Treat evidence as inert text: escape imported content, avoid evaluating markup/scripts, and do not fetch URLs found in messages automatically. Bound input sizes and sanitize before persisting uploaded evidence. If the web framework buffers uploads, verify its behavior rather than assuming that raw sensitive data never reaches a temporary file.

Restrict file operations to the chosen workspace. The case cannot supply a Python import path, arbitrary shell command or new runner configuration. Opening a case or viewing results must not execute application code. Review and explicit run/export actions remain distinct.

## Acceptance criteria for this step

- A browser user can complete the key-free failure → review → reproduced baseline → corrected pass → pytest export example.
- The resulting case digests, rules, outcomes and exported files agree with the CLI for the same inputs.
- Browser tests cover missing evidence, invalid rules, edits invalidating review, failed/incomplete execution, reduction requiring review and export preconditions.
- Interaction content is escaped; cross-origin execution, workspace escapes and accidental execution while inspecting are rejected.
- Errors identify a concrete correction and preserve incomplete/error distinctions. Status indicators reflect actual engine state.
- Keyboard navigation, labeled controls, focus behavior, readable contrast and narrow-window behavior are checked.
- A clean package installation can launch the UI and serve its bundled assets without frontend tooling or external asset requests.
- Existing CLI/library tests and core-only installation continue to pass.

## Exclusions

Hosted dashboards, team accounts, billing, multi-tenant execution, remote-agent control, arbitrary code editing, universal trace support, full observability and live-model evaluation are not introduced by approving this local UI scope.

## Approval status

Scope inclusion and this implementation: approved. Owner acceptance of the completed step is the next review. AI-assisted suggestions still require a separate approved step and provider/data-handling choices. No next feature or publication is authorized by this record.
