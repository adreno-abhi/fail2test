# Hosted CI and repository controls

27 October 2026. The repository remains private at `adreno-abhi/fail2test`. The owner
approved verifying included Actions quota, running hosted CI and applying available
repository controls without a paid upgrade or public-visibility change.

## Account and repository checks

Included Actions quota and a zero-paid-usage stopping budget were verified in the account
UI before enabling CI. No billing settings, payment method, plan or account-wide permission
was changed. Exact account usage figures remain in private local audit output.

Repository Actions policy permits owner actions and only these external action revisions:

- `actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803`
- `astral-sh/setup-uv@18d369b23da25a81e9458561248e1aafff6a70fa`

Full-length SHA pinning is required. Blanket GitHub/Marketplace creator permission is off.
Default workflow tokens remain read-only, workflow PR approval/creation is off, private
fork workflow execution is off, cross-repository workflow access is off, and retention is
seven days. No provider, registry or publishing credentials were added.

The branch-rules UI explicitly states that rulesets will not be enforced on this private
repository under the current GitHub Free plan. No unenforced ruleset was created or
presented as protection, and no upgrade was purchased. The planned `main` policy remains
PR-based changes, required `ci-complete`, resolved conversations and blocked force pushes/
deletion, with zero required outside approvals while there is one maintainer. Apply and
verify it during a separately approved public setup, when supported.

## First hosted run and cold-cache diagnosis

[CI run 40473981074](https://github.com/adreno-abhi/fail2test/actions/runs/40473981074)
tested `main` revision `2c55665`. All six core/native/HTTP matrix jobs passed on Ubuntu 22.04
and Windows Server 2022, each with Python 3.12, 3.13 and 3.14. The Windows quality job passed
its tests including Chromium, lint, formatting, types, strict docs, community/inventory
checks and build, then failed at installed-artifact smoke verification.

The failure was `pydantic was not found in the cache`. `uv sync --locked` had installed
packages, but the subsequent `uv pip install --offline` needed resolver/index metadata
that was absent in this clean runner cache. A local run with a new `UV_CACHE_DIR`
reproduced the same failure before the fix. Re-running without a change was not a remedy.

The correction permits registry downloads for package installation, while constraining
core wheel, source and optional native dependencies to exported lock versions. Core is
still checked before LangGraph is installed, and the application workflow itself remains
key-free with no provider calls. Subprocess logs are decoded explicitly as UTF-8.
CI now assigns the smoke step a dedicated fresh cache so this boundary stays exercised.
The corrected harness passed the full core/source/native smoke workflow locally with a
different initially empty cache.

The first repair run then passed package smoke and exposed a second acceptance-harness
issue: on Windows, the installed module path was resolved but `sys.prefix` was not. A
temporary directory using an actual 8.3 short-path spelling reproduced the same installed-
origin assertion failure locally. Resolving both sides preserves the outside-checkout
guard while recognizing two spellings of the same virtual environment. This correction
does not permit an unrelated source checkout to pass the origin check.

## Repair acceptance and merged-main verification

[PR #3](https://github.com/adreno-abhi/fail2test/pull/3) passed all 16 push/PR checks at
`1aa95f0ce44586ec0344585b9df6dbc6f6df9c27`, then the owner approved its merge.
The merge used the configured ID-based GitHub noreply identity, preserving the reviewed
source tree exactly. The browser merge form was cancelled because it proposed personal-email
attribution; no personal address was included in the merge commit or this record.

Merged `main` revision `345eced5b4a1343998adde6b17f8c090ff960d74` passed
[CI run 40476938192](https://github.com/adreno-abhi/fail2test/actions/runs/40476938192)
in 3m35s. All six test-matrix jobs, the quality/browser/package job and `ci-complete`
succeeded. Quality included installed-artifact smoke and the installed CLI/browser/native
acceptance workflow. These are results for the merged source, not a rerun of unchanged
initial `main`. No provider calls, releases or paid services were added.

Public/contact/security-feature checks and final publication approval remain pending.
Dependabot PRs are not automatically merged. Hosted CI success does not itself establish
branch enforcement, vulnerability reporting, independent usability or production safety.

## Primary references

- [Included usage and stopping budgets](https://docs.github.com/en/billing/reference/product-usage-included)
- [Branch protection availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
