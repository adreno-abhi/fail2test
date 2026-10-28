# Security policy

## Supported versions

No public release has shipped. During local development, security fixes target the current
development branch. After first publication, the latest published release will receive fixes
or upgrade guidance; older versions have no promised backport window. A compatibility/support
matrix must be confirmed in release notes before claiming a broader maintenance commitment.

## Report privately

Do not put exploit details, keys, private evidence or sensitive code in public issues/PRs.
Use [Security → Report a vulnerability](https://github.com/adreno-abhi/fail2test/security/advisories/new).
Private vulnerability reporting was enabled and its public entry point verified on
28 October 2026. A GitHub sign-in may be required. This sends a private report to the
repository maintainers; do not use an ordinary issue for sensitive details.

No personal email or fallback mailbox is published. If GitHub's reporting control is
unavailable, request restoration without including vulnerability details. Never infer
an address from Git history or send security details through the conduct/abuse route.

Include affected commit/version, Python/OS/dependency versions, impact, reproduction steps,
expected boundary and a minimal synthetic case. State whether application code was trusted,
which operation ran, and whether a provider received data. Do not send live credentials;
revoke exposed credentials with the issuing service first.

The maintainer assesses reproduction, impact and remediation, coordinates privately, credits
reporters with consent and publishes an advisory when a fix/mitigation and disclosure plan
are ready. Timing depends on severity and capacity; no SLA, fixed disclosure deadline or
bug bounty is promised. Ask for status through the same private route. If it is unavailable,
do not move sensitive details to a public issue merely to obtain attention.

## Trust boundaries

- Runner configuration, application code, dependencies and pytest plugins are executable and
  trusted. Worker supervision is process control, not hostile-code or network isolation.
- Evidence is data. Import sanitizes known fields/patterns in memory; detection is best effort.
  Substitution can change behavior. Review saved artifacts and AI previews before sharing.
- Strict fixtures never silently fall through to real model/tool clients. Missing interactions,
  swallowed transport errors, unsupported execution and timeouts remain incomplete.
- Review/validation digests bind case content, not identity or provenance. A local owner can
  modify cases and manifests. Runner hashes cover the configured module, not its entire closure.
- The UI is explicitly started on loopback, with session/origin/Host controls and contained
  paths. It is not intended for remote hosting, proxies, tunnels or shared untrusted machines.
- Default fixture operations have no provider telemetry. Optional AI sends the previewed
  sanitized fields only after explicit consent. Profile destinations and credentials are
  owner-controlled; provider policies apply. Model output is untrusted and never auto-approved.
- Free-only routing controls are operational limits, not a provider billing or privacy guarantee.
  Do not relax an account's privacy policy automatically to make a test succeed.

Report a bypass of the documented controls. Operations deliberately performed by trusted
application code may instead be an application boundary; provide the smallest reproducer so
the maintainer can assess it. Do not test against someone else's systems without permission.

Detailed contracts: [privacy and limitations](docs/site/contracts.md),
[local UI](docs/site/local-ui.md), [AI suggestions](docs/site/ai-suggestions.md).

Host reference: [GitHub private reporting instructions](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately).
