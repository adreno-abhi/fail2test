# Security, privacy and trust model

## Security objectives

Protect local sensitive evidence, prevent data artifacts from becoming executable instructions, make controlled execution honest, and secure the project's release chain. Fail2Test is a testing tool. Its ordinary Python process is not a sandbox for hostile application code.

## Trust domains

1. **Untrusted evidence:** traces, imported model output, tool text, case files downloaded from others, filenames, and report content.
2. **Reviewed project configuration:** runner import paths and local execution settings. Loading this configuration must not import code until an execution command is requested.
3. **Executable application:** the runner, dependencies, pytest plugins, `conftest.py`, and repository scripts. Running them has the privileges of the execution environment.
4. **Optional model provider:** a future external recipient of an explicitly chosen sanitized payload. It is not part of the default local path.
5. **Release infrastructure:** GitHub workflows, maintainers, package registry identities, signing/attestation systems and dependency sources.
6. **Future hosted executor:** a separate design requiring hostile-code isolation, tenancy and data-governance controls; absent from the alpha.

## Threat/control/verification matrix

| Threat | Required control | Verification |
|---|---|---|
| Trace text asks the tool to run commands or reveal secrets | Treat all evidence as data; no instruction precedence; no automatic model tools | Injection strings remain inert through import, proposal and export |
| Code injection through assertion/template | Closed rule DSL, fixed exporter templates, validated identifiers, escaped strings | Adversarial quotes/newlines produce valid inert Python literals; generated AST contains only approved template structure |
| Malicious serialized objects | JSON only; no pickle, unsafe YAML constructors, arbitrary checkpoints, or dynamic schema fetch | Rejected formats and executable-looking payload tests |
| Fixture path traversal/symlinks | Resolve explicit paths; task writes contained in output directory; no archive support initially | `..`, absolute path, symlink escape and overwrite tests on supported platforms |
| Sensitive fields leak in fixtures/reports | Structured deny paths, pattern detection, bounded previews, reviewable sanitization diff | Synthetic canary credentials absent from every exported/log artifact |
| Sanitization changes semantics | Sensitivity/replacement lineage, revalidation, explicit incomplete state | Redacted routing/argument inputs cannot retain old validation claims |
| Mock falls through to real tool | No live fallback in fixture transport | Unknown-call tests and reference isolated network-disabled CI run |
| Arbitrary user code bypasses injected dependencies | Explain instrumentation limits; only declared supported execution gets a scoped claim | A bypass example is documented; no whole-host safety guarantee |
| Hostile code in pull requests | No secrets for fork jobs; restricted tokens; approved workflow changes; isolated ephemeral tests | CI policy review and fork smoke test |
| Compromised dependencies/actions | Reviewed locks, automated updates, scanning, verifiable release artifacts | Lockfile review, SBOM/license inventory, attestation verification |
| Published artifact differs from reviewed source | Protected publishing identity, exact artifact promotion, attestations, immutable release assets when supported | Install/verify artifact associated with expected tag and workflow |
| Resource exhaustion | Input/payload/depth/run/time caps, bounded subprocess output | Large/malformed fixture and timeout/cancellation tests |

## Local data lifecycle

- Import reads user-owned source data without mutation. Prefer structured sanitization before any new persistent artifact. Temporary buffers and previews remain bounded.
- Default result logging stores IDs, types, sizes, hashes and redacted diagnostics. Raw prompts/tool outputs are not written into general logs.
- A local raw-capture mode is not part of the alpha; explicit capture hooks should support allowlisted fields and immediate sanitization. If raw capture is added later, it requires explicit opt-in, a separate directory, retention guidance and prominent sensitivity labeling.
- Sanitization is best effort. No detector can guarantee all secrets, personal data or proprietary content are removed. Users review the final export before committing or sharing.
- Stable placeholders preserve identity equality where possible. They do not prove semantic equivalence. Where a value affects routing, require a reviewed synthetic replacement and new reproduction evidence.
- No background upload, analytics endpoint, crash reporter or telemetry identifier in the alpha. Local opt-in debug files require a visible destination and sensitivity notice.
- Filesystem permissions use user-private defaults where supported; actual access also depends on host permissions and backup/sync settings. Do not claim encryption at rest beyond what the host supplies.
- A cleanup command, if implemented, previews exact task-owned paths; original trace sources and committed test cases are never implicitly removed.

## Model-assisted analysis, later

Before enabling a provider: show destination/provider, included fields, excluded fields, estimated request size, request limit and cost policy. Use an explicit user-selected configuration; no automatic selection of credentials found on the machine. Do not commit keys, print values, place keys in cases, or include them in error traces. Provider calls have timeouts and capped retries; invalid proposals remain unapproved data.

A provider outage must leave rule editing, fixture runs and test export usable. A model cannot grant approval or expand tool/network access. A provider request/response audit contains hashes and redacted metadata by default. Legal/privacy terms for actual provider processing must be selected with the deployment; the plan does not invent a data-processing agreement.

## Execution safety

Subprocess separation aids termination and state hygiene; it is not a security isolation guarantee. Docker with read-only mounts, limited resources and disabled network can improve containment for trusted/synthetic examples, but is not a complete hostile-code sandbox or cross-platform security guarantee. Document exactly what a supported execution environment enforces.

An execution error, incomplete interaction, or unsupported capability must not become a passing assertion. Do not label a case “safe” because no known dangerous calls appeared. Scope reports to the observed injected interfaces and the selected rule.

## Security reporting and response

Before publication enable GitHub private vulnerability reporting and fill the contact information in the publication template. Do not invent a security email or claim monitored infrastructure. Recommend acknowledgement within five business days as a best-effort maintainer goal, with no 24/7 SLA. Triage exploitability, affected supported versions, reproducer sensitivity and dependencies. Coordinate a patch and advisory; avoid publishing live customer traces or exploit-enabling secrets.

At alpha support the latest alpha only, with critical fixes or upgrade guidance for earlier versions. Stable support policy is published before 1.0 and must match actual maintenance capacity. Maintain a private incident checklist, maintainer recovery path and release revocation procedure.

## Hosted service prerequisites

No customer-code hosting before a separate security gate covers tenant authorization, credential separation, egress policy, hardened ephemeral execution, quotas, encryption/key ownership, retention/deletion, backups, audit records, incident response, dependency execution and abuse. Ordinary Kubernetes namespaces or subprocesses alone are insufficient isolation claims. Customer-managed runners are an option, not a way to skip control-plane authorization or artifact/data security.

Sources: [MCP security policy](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/SECURITY.md), [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use), [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/).
