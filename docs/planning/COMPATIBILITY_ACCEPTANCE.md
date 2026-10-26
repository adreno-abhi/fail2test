# Compatibility and first-use acceptance contract

26 October 2026. Owner approved this local verification step. No GitHub/registry setup or
provider/local-model work is included. Existing private contact deferral remains in force.

## Direction and build scope — PASS

Measure the declared Python 3.12–3.14 range with real isolated interpreters and the lockfile.
Use Windows and the existing Ubuntu WSL environment; distinguish WSL from hosted Linux CI.
Run core/native/HTTP tests on each, with full Chromium coverage on the available Windows
browser environment. Explicitly identify untested OS/browser/dependency combinations.

Fresh-wheel trials run outside the checkout, verify installed-package origin, reproduce broken
code, pass the fix, reduce/export, and run ordinary pytest. Browser control uses development
Playwright while its server runs the clean installed wheel with core dependencies only.
The native example is copied outside the checkout and its production factory remains unchanged
for adoption. Reintroduce a synthetic bug, require the unchanged export to fail behaviorally,
restore the original bytes and require it to pass again. Never weaken fixture/review checks.

Existing tests are the feedback loop for compatibility failures. Diagnose failures before
changing bounds; exclude mistakenly selected interpreters or broken harness trials from
passing evidence. Check lower direct dependency bounds separately; passing current locked
versions does not establish the whole dependency range.

## Operation and acceptance — PASS

Use managed Python/tooling in isolated test directories; do not change default system Python,
upgrade the operating system, start Docker services or install/start an AI runtime. Package
downloads are permitted; model/provider calls are not part of this step. Export no credentials
or machine-specific paths into committed reports. Timings are single automated wall-clock
trials with cached dependencies, not human onboarding benchmarks or performance guarantees.

Record interpreter/package versions, counts, skips, failures and fixes. Update current docs and
public support claims to the evidence. Keep human reading/integration effort and missing
host environments explicit. A local acceptance result does not authorize publication.
