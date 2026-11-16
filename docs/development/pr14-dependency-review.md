# Dependabot PR #14 local review

Reviewed 16 November 2026 by Codex with owner authorization for local testing and fixes.
PR: https://github.com/adreno-abhi/fail2test/pull/14
Reviewed head: `10ff316524c65e612a8a78d40cd0a2c8f8ec2c20`.
Base: `41ddbc54ee8189bbce784bc5293a83d6d0d48166`.

## Decision

The dependency changes pass local Windows/Python 3.13.5 verification with the inventory
correction described below. They are suitable to advance to hosted CI review; this is not
approval to merge an untested remote head. No remote branch, PR or repository setting was
changed during this review. Other Python/OS combinations still need the required matrix.

## Changes and correction

The PR updates ten direct dependencies, Pydantic Core transitively, adds `ast-serialize`
and removes `pyee` from the lock. The explicit constraint change permits mypy 2.x.
The original PR failed `scripts/dependency_inventory.py --check-lock` because the
inventory retained the old lock hash and versions. Regenerated both licensing inventories
from the exact installed environment and reviewed their diff. All 82 third-party lock
entries now match. New `ast-serialize` distribution metadata declares MIT; both included
license files were inspected and their hashes recorded. No new license exception found.

Pydantic 2.14.3 includes the fixes first released in 2.14.2 for
[GHSA-qpmf-fgh3-ff25](https://github.com/pydantic/pydantic/security/advisories/GHSA-qpmf-fgh3-ff25)
and [GHSA-3r8g-cqwr-jr29](https://github.com/pydantic/pydantic/security/advisories/GHSA-3r8g-cqwr-jr29).
Their affected configurations do not establish an exploitable path in this project.
This review is not a complete dependency vulnerability audit. The PR refreshes the lock;
it does not change the package's existing Pydantic lower bound or the v0.1.0 release tag.

## Results

| Check | Final local result |
| --- | --- |
| Locked full environment including browser/native extras | Pass |
| Ruff lint and format | Pass; 130 files formatted |
| mypy 2.4.1 | Pass; 20 source files |
| Strict MkDocs build | Pass |
| Repository publication structure | Pass |
| Dependency inventory consistency after correction | Pass; 82 packages |
| Full pytest including real Chromium | 211 passed in 161.92 seconds; 89% coverage |
| Wheel and source distribution build | Pass |
| Clean wheel/source/native smoke | Pass when run alone |
| Installed CLI, browser and native acceptance | Pass when run alone; no provider calls |

Installed acceptance confirms that an unchanged exported test detects the bug and passes
the fix. CLI workflow: 14.481 seconds; browser workflow: 8.078 seconds; native workflow:
26.430 seconds; total: 54.063 seconds. These are automated local timings, not human
onboarding measurements. Playwright 1.65.1 downloaded its Chromium 158 build for the tests.

## Initial failures and limits

The first full run returned 210 passes and one HTTP test failure, a Windows connection
abort in `test_origin_required_and_preflight_rejected`. The unchanged test passed alone.
Initial package smoke and installed acceptance also timed out starting the native runner
while heavy checks overlapped. Both passed sequentially with original timeout values.
The subsequent full sequential run passed all 211 tests. Contention/timing is a plausible
explanation, not a proven root cause; retain this history and watch for recurrence in CI.
No assertion, application source, fixture contract or timeout was weakened.

Machine-local reports are under ignored `local-artifacts/package-smoke.json` and
`local-artifacts/pr14-installed-acceptance.json` in the isolated review worktree. No keys,
customer evidence or model requests were used. Final hosted CI, remote inventory correction,
merge and any patch release remain separate owner-approved steps.
