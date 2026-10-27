# Key-free quickstart

Run from the Fail2Test checkout. Install [uv](https://docs.astral.sh/uv/) and a supported
Python interpreter. Clone the repository as shown in its README, then `cd fail2test`.
This example uses synthetic data and no payment service or model API. The core example
does not need the optional LangGraph dependencies.

```text
uv sync --locked
uv run fail2test init local-artifacts/demo
uv run fail2test import local-artifacts/demo/failure.json --out local-artifacts/demo/case
uv run fail2test inspect local-artifacts/demo/case --json
uv run fail2test review local-artifacts/demo/case --reviewer local-owner
uv run fail2test validate local-artifacts/demo/case --runner broken --config local-artifacts/demo/fail2test.toml
```

The model fixture contains two identical refund actions. The broken application dispatches both. `validate` returns exit 0 **because it reproduced the selected failure**. This is different from a regression run passing.

Run the broken version explicitly:

```text
uv run fail2test run local-artifacts/demo/case --runner broken --config local-artifacts/demo/fail2test.toml
```

Expect `complete: fail` and exit 1. Now run the corrected application with the same reviewed case:

```text
uv run fail2test run local-artifacts/demo/case --runner fixed --config local-artifacts/demo/fail2test.toml
uv run fail2test export local-artifacts/demo/case --runner fixed --config local-artifacts/demo/fail2test.toml --out local-artifacts/demo/tests
uv run pytest local-artifacts/demo/tests/test_regression.py -q
```

Expect `complete: pass` and a passing pytest test. The exported test imports the current application runner. It does not simply assert against the original trace. The integration suite also edits application code while leaving the exported test unchanged to verify that distinction.

## Reduce irrelevant context

```text
uv run fail2test reduce local-artifacts/demo/case --runner broken --config local-artifacts/demo/fail2test.toml --out local-artifacts/demo/reduced --max-runs 8
```

Reduction re-executes candidates, removes unnecessary input fields and preserves the selected failing rule. The execution budget includes the baseline recheck. The reduced case is a new unapproved artifact: review and validate it before export. Current reduction covers input deletion, not arbitrary tool/model-sequence minimization.

## Propose and review rules

```text
uv run fail2test propose local-artifacts/demo/case --out local-artifacts/demo/proposal.json
```

Read and edit the proposal's requirement, then use `review --rules PATH --reviewer LABEL`.
Candidates are not business truth and are never automatically approved. The `propose` command
is deterministic and makes no model calls. [Optional AI suggestions](ai-suggestions.md) use
separate preview/consent commands. See [compatibility and acceptance](compatibility.md) for
verified environments and the distinction between automated timings and human first-use effort.

All output directories must be new. Original inputs are not overwritten. The reviewer label is a local acknowledgement, not a verified identity or signature.

## Move from the demo to your application

First check [whether your application fits](adoption.md), then prepare
[supported evidence](evidence.md) and [register a runner](integration.md). The names
`broken` and `fixed` belong to the demo. In your application, use one runner name,
validate the failure, make the fix in your editor and rerun that same runner/test.
The model/tool responses remain recorded fixtures throughout.
