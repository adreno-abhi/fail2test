# Compatibility and acceptance

The declared Python range is **3.12–3.14**. These environments were actually checked on
26 October 2026 with locked dependencies. Patch versions identify trials, not exclusive support.

| Environment | Python | Core/native/HTTP tests | Real browser tests |
|---|---|---|---|
| Windows 11 x64 | 3.12.13 | 182 passed | Not run on this interpreter |
| Windows 11 x64 | 3.13.5 | 182 passed | 6 passed; 188 total, 88% coverage |
| Windows 11 x64 | 3.14.3 | 182 passed | Not run on this interpreter |
| Ubuntu 20.04.6 x64, WSL2 | 3.12.13 | 182 passed | Not run |
| Ubuntu 20.04.6 x64, WSL2 | 3.13.12 | 182 passed | Not run |
| Ubuntu 20.04.6 x64, WSL2 | 3.14.3 | 182 passed | Not run |

Selected suites had zero failures/errors/skips. Browser tests were explicitly excluded from
non-browser rows. WSL uses Linux Python/POSIX processes, but is not hosted CI or proof of every
Linux distribution. macOS, ARM, other browsers and Linux browser dependencies remain
unverified. The verified browser setup is Playwright 1.64.1 with its Chromium 156 build.

## Hosted verification

On 27 October 2026, merged `main` revision `345eced` passed
[GitHub CI](https://github.com/adreno-abhi/fail2test/actions/runs/40476938192): Ubuntu 22.04
and Windows Server 2022 on each of Python 3.12, 3.13 and 3.14. The Windows/3.13 quality
job also passed Chromium tests, wheel/source/native smoke and installed CLI/browser/native
acceptance. The repository remains private, so this evidence link currently needs access.
This adds hosted evidence to the dated local matrix; it does not add macOS/ARM or Linux-browser claims.

## Dependency boundaries

Runtime floors are Pydantic 2.10, rfc8785 0.1.4 and Typer 0.16. The native extra requires
LangGraph 1.2+ and langchain-core 1.4+, below their next major versions. This corrected
direct-minimum combination also passed 182 tests on Windows/Python 3.12.13 with pytest 8.3.0.
Transitive versions were resolver-selected; this is not a lowest-transitive or exhaustive
Cartesian-product compatibility claim.

The old Typer floor allowed CLI help to fail with current Click. The old graph range allowed
an incompatible prebuilt/runtime combination importing missing `ExecutionInfo`. Metadata
was tightened after reproducing those failures. No assertion, fixture or review/error control
was weakened. The standard native lock uses LangGraph 1.2.17 and langchain-core 1.7.0.
See [integration](integration.md) for synchronous/serial text/tool scope and exclusions.

## Installed-package first-use trials

Fresh virtual environments installed the built wheel outside the source checkout and verified
its import origin. CLI trials reproduced broken behavior, passed the fix, reduced/exported
and ran ordinary pytest. Native dependencies were added after proving core use without
LangGraph. The browser controller used development Playwright; the installed UI server
needed no Node/build tools or browser-automation dependency.

| Automated Windows / Python 3.13 trial | Wall time |
|---|---|
| Core CLI workflow, after installation | 9.744 seconds |
| Installed UI launch → review/baseline → fixed pass → export/pytest | 6.862 seconds |
| Native workflow including reintroduced-bug detection/restoration | 21.357 seconds |
| Complete trial including environment and package setup | 41.743 seconds |

These are single automated trials with cached/download conditions and concurrent host activity.
They exclude human reading, assertion decisions, evidence capture, application refactoring and
prerequisite installation. They establish operability, not human onboarding time or a latency
SLA. PLAN.md's under-ten-minute tutorial / roughly-thirty-minute integration goals still need
a human trial or explicit owner acceptance of the remaining usability uncertainty.

The prepared native sample already accepts model/tool injection. Adoption adds a ten-nonblank-
line runner, TOML and fixtures with zero production-factory changes; this does not predict
effort for a legacy application without injection. Its unchanged exported test failed when a
duplicate-dispatch bug was reintroduced, then passed after restoring original application bytes.

## Reproduce

The owner subsequently confirmed the guided sample UI path through saving an export, after
clarifications to import and export prerequisites. This is human sample acceptance, not an
independently timed onboarding or real-application adoption study. Timing targets remain
unmeasured for the human trial; the table above remains explicitly automated evidence.

```text
uv sync --locked --all-extras --group browser
uv run --group browser playwright install chromium
uv build
uv run --group browser python scripts/acceptance.py --browser --out local-artifacts/acceptance/my-trial.json
```

`--python 3.12` or `--python 3.14` selects the target fresh environment; the browser controller
can stay on the development interpreter. Omit `--browser` for CLI/native-only trials. Reports
record wheel identity, expected/actual exit codes, timings and explicit human/provider flags.
Choose a new output filename. No provider key or local AI runtime is required or installed.

For a source-test interpreter, invoke the selected environment directly:

```text
uv sync --locked --all-extras --python 3.12
.venv/Scripts/python.exe -c "import sys,langgraph; assert sys.version_info[:2] == (3,12)"
.venv/Scripts/python.exe -m pytest --ignore=tests/test_ui_browser.py -q
```

On Linux use `.venv/bin/python`. Set a separate `UV_PROJECT_ENVIRONMENT` for concurrent
matrices. A later `uv run` without matching Python/extra selection can recreate an environment
using the default interpreter, so verify the executable and native imports before counting tests.

Use `scripts/constraints/minimum.txt` for direct-lower-bound experiments in a separate
environment with the built wheel and test dependencies. Record transitive resolution too;
do not replace the main lockfile with a boundary experiment.
