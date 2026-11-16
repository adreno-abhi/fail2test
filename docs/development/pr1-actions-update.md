# PR1 workflow action update

16 November 2026. Updates CI and documentation workflows together:

- actions/checkout v7.0.1: `3d3c42e5aac5ba805825da76410c181273ba90b1`
- astral-sh/setup-uv v10.3.3: `68559e99cc807c1eb7e9238fd43a15bba460eec2`

Both SHAs were checked against the upstream release tag refs and action manifests.
Both use node24. Checkout v7 protects privileged fork checkout paths; no unsafe
checkout opt-in is needed for ordinary PR CI or our main-only, same-repository
push-gated documentation workflow. Setup-uv retrieves manifests from the Astral
mirror with GitHub fallback. The selected uv version remains 0.10.9.

The existing PR branch incorporates main without rewriting its history. Pages was
added after the original PR and now uses the same reviewed pins as CI. No runtime
code, package lock, token permissions, triggers, job guards, credential persistence,
cache settings or test assertions change.

Repository policy must allow the two exact revisions above before hosted validation.
Retain existing pins during transition and all other narrow policy controls. Hosted
CI on the final PR head is required before proposing merge; static checks do not
prove GitHub runner execution. Verify Pages after an approved merge.

References: [checkout release](https://github.com/actions/checkout/releases/tag/v7.0.1),
[setup-uv release](https://github.com/astral-sh/setup-uv/releases/tag/v10.3.3).

Local validation: both workflow YAML files parsed successfully; structural comparison against main confirmed only the two action pins changed. Ruff passed and mypy passed for 20 source files. Full application suite is delegated to final PR CI; no application code changed.
