# Contributing to Fail2Test

Thank you for helping turn real agent failures into useful regression tests. Code, documentation, synthetic failure examples, accessibility/usability feedback, integration maintenance and careful bug reports are welcome.

This is a publication draft. Follow the implementation repository's tested setup instructions once available.

## Before starting

- Read the supported scope, code of conduct, security policy and roadmap.
- Use issues for reproducible bugs and focused enhancements; use Discussions for usage questions when enabled.
- Discuss public schema/interface, execution, privacy or major architecture changes in an RFC before a large PR.
- Never post real API keys, private traces, customer information or proprietary code without rights and permission. Use a minimal synthetic reproducer.

## Setup and checks

The intended setup is `uv sync --locked --all-groups`; checks are Ruff, type checking, pytest and the strict docs build described in the developer guide. These commands must be verified against actual project files before this template is published. Docs-only contributors should have a smaller documented setup.

## Pull requests

Keep changes focused and link the issue. Explain behavior before and after, attach relevant validation, update docs/changelog, and note compatibility/security impacts. Tests must exercise current application code when claiming regression behavior. Do not edit approved rules or fixtures solely to hide a failing test.

Sign off commits using `git commit -s`. This records agreement with [Developer Certificate of Origin 1.1](https://developercertificate.org/). Contribute only material you have rights to submit under Apache-2.0. You retain copyright; no separate broad CLA is required at launch under the proposed policy. If a sign-off is missing, maintainers explain how to correct the commits; do not add someone else's sign-off for them.

AI-assisted work follows the same requirements. Understand and verify your change, provide provenance where material, and do not submit unexplained generated code or private prompt content.

## Review

Maintainers review correctness, scope, test evidence, usability, privacy and maintenance cost. Substantial design disagreements go to the RFC process. Reviews are best effort and may take longer when maintainer capacity is limited. A paid request does not bypass review.

## New contributors

Look for `good first issue` and `help wanted`. Good first tasks include a synthetic fixture for an existing rule, a clearer error, a tested docs improvement, or a bounded platform reproduction. Ask before starting an unassigned large change; maintainers can help identify a smaller contribution.

## Security and conduct

Report vulnerabilities through the private route in SECURITY.md. Report conduct concerns through the verified enforcement contact in CODE_OF_CONDUCT.md. Ordinary issue templates are not private reporting channels.
