# Developer adoption and launch-readiness review

27 October 2026. Reviewed source baseline: merged `main`
`345eced5b4a1343998adde6b17f8c090ff960d74`. Initial review commit `54d71a0` contained
documentation changes only. The repository stays private. This is a maintainer/AI-assisted assessment,
not independent customer research, a penetration test or a prediction of GitHub popularity.

**Subsequent approved correction:** the packaging finding below is fixed and verified
locally; see [packaging correction](packaging-scope-fix.md). Original findings and probe
results below describe the reviewed baseline. Hosted checks for the correction remain pending.

**28 October update:** the packaging correction subsequently merged as `53727aa` and
passed [hosted CI](https://github.com/adreno-abhi/fail2test/actions/runs/40486569110).
The separately approved [safe case diagnostics](safe-case-diagnostics.md) address the
field-location and unknown-key disclosure finding locally; their new hosted checks remain pending.

## Recommendation

The core is useful for a specific audience: Python developers who have a reproducible
agent orchestration failure, can inject model/tool dependencies, and want a durable pytest
regression. It has a working end-to-end path and more than repository scaffolding.
I would try it for a repeated action or forbidden-tool incident in a supported application.

I would hesitate if I expected to upload a production trace and receive a working test
automatically. Evidence conversion and runner integration are manual. I would choose another
approach for live prompt/model comparisons, async/streaming agents or unsupported stateful replay.
Positioning it as a universal agent failure recorder would overpromise its current usefulness.

Do not switch visibility as part of this review. An archive-inspection check found a
**release blocker: the reviewed source-build selection could include ignored local files**.
The subsequent approved correction addresses that boundary locally. Finish hosted verification,
the high-priority adoption items,
final source/security/release checks and exact-candidate approval.
A complete first release can remain narrow; supporting every framework is not a prerequisite.

## Audience and job to be done

| Developer | Usefulness today | Likely reason to leave |
|---|---|---|
| Python agent maintainer fixing orchestration/tool-dispatch logic | Strongest fit: the same recorded response can expose the bug and verify the code fix |
| LangGraph developer with sync text chat and injectable model/tools | Good fit within the explicit adapter scope |
| Platform/test engineer maintaining incident regressions across PRs | Reviewable JSON and ordinary pytest can fit existing review/CI practices |
| Developer changing prompts/models and measuring answer quality | Recorded requests/responses do not evaluate the new model; strict requests may mismatch |
| Developer with only vendor traces, log text or screenshots | Manual conversion is a substantial first-use barrier |
| Async/streaming, parallel, multimodal or JS/TS agent developer | Required execution is outside current support |
| Legacy application with hardcoded clients/database state | Injection/setup effort may exceed the benefit of adding this tool |

The concrete job is: “This incident should fail in CI if my code reintroduces the behavior,
without repeatedly contacting the model or real tool service.” The product should sell that
outcome before describing rule engines, provenance or optional model providers.

## What was actually exercised

- Read the rendered private GitHub repository, README, user guides, contribution/release
  policies, runtime import/matching/export contracts and maintained native example.
- Verified the existing hosted evidence: all six Ubuntu/Windows Python jobs, Windows
  Chromium suite, package smoke, installed acceptance and `ci-complete` passed on the
  reviewed merged source. [Exact run](https://github.com/adreno-abhi/fail2test/actions/runs/40476938192).
- Created a fresh Python 3.13 environment outside the package source path, installed the
  built core wheel and pytest, checked import origin and absence of LangGraph, and followed
  init/import/review/baseline/export/pytest. The packaged synthetic demo passed.
- Authored a different synthetic application: a read-only agent whose recorded plan
  requests `delete_document`. Added one runner/config/case, reproduced the forbidden-tool
  failure, exported against that runner, then edited only application code. The unchanged
  exported pytest failed before the fix and passed afterward. Copying the complete
  application tree to another directory preserved the passing export.
- Tested malformed evidence and stale review. Both were rejected. The malformed case
  returned `INVALID_CASE` with a generic message and no field location, confirming the
  diagnostic gap rather than assuming it from the source alone.
- Validated the new evidence-guide JSON and command sequence against the actual importer
  and CLI as part of this documentation review; results are summarized in the verification
  section below after checks complete.

The fresh-app probe used a maintainer-authored synthetic scenario and already understood
the API. It is additional operability evidence, not a real customer integration or an
unassisted onboarding study. It does not establish the ten-/thirty-minute human targets.
No provider request, local model installation or real deletion/payment operation was needed.

## Findings and priority

| Priority | Finding and evidence | Effect on adoption | Disposition |
|---|---|---|---|
| Blocker | Source archive contained 225 members under ignored `local-artifacts/`; a minimal ignored nested-`tests` marker reproduced inclusion | Locally built source releases can contain unintended files even when Git is clean | Open: quarantine unpublished builds; use explicit root-path selection and add negative archive checks before release |
| High | README lacked a clear audience/fit decision, clone instructions and expected output; important limits appeared after substantial detail | Visitors cannot quickly decide whether trying it is worthwhile | Corrected locally in this review |
| High | Moving from demo to incident required a custom case/neutral trace and runner, but the clearest evidence explanation was inside the UI guide | “Upload a failure” suggests easier integration than exists | Added fit/evidence guides, full neutral JSON and explicit manual-conversion language; no recorder was implemented |
| High | Invalid case errors suppress both values and field location; actual malformed-rule probe returned generic `INVALID_CASE` | Users hand-authoring strict JSON cannot readily find the bad field | Addressed locally in the approved [safe diagnostics step](safe-case-diagnostics.md); hosted verification pending |
| High | Independent existing-application adoption is unmeasured; owner trial was guided and used the maintained example | We cannot support broad “easy integration” or timing claims | Open: independent trial recommended; owner may explicitly accept the documented uncertainty instead of inventing evidence |
| High | Security reporting/public protections and final release review are still pending | Trust and reporting routes must match the public repository | Open host/release work; keep gate closed |
| Medium | Every model request is matched exactly; prompt/tool-schema edits can invalidate fixtures | Some developers will interpret mismatch as a broken test generator | Explained earlier; keep errors distinct from behavioral failures and live evaluation |
| Medium | Python 3.12+ and sync/serial text scope excludes other common application shapes; macOS/ARM has no acceptance evidence | Developers may be unable to use the current adapter unchanged | Publish the fit matrix; add support only with demand and acceptance evidence |
| Medium | “Portable pytest” can imply no library/config dependency, but generated source imports Fail2Test and references relative local config | Moving only the export or omitting the runtime breaks CI | Documented exact file/runtime requirements and verified complete-tree relocation |
| Medium | Separate demo `broken`/`fixed` runners can suggest that every adopter maintains two applications | Confuses how to fix real code and retain a regression | Explained one-runner workflow; exercised an in-place application fix |
| Medium | No public install artifact, concise visual demo or independently measured time-to-value | Adds friction for discovery, trying and sharing | Source installation documented; release/version/distribution and a short real demo remain launch-preparation choices |
| Medium | Setup, contribution and status documents still said no repository or CI existed; CONTRIBUTING described obsolete offline package smoke | Contradictions reduce trust and confuse contributors | Updated current documentation; kept dated historical evidence clearly scoped |
| Low | Many planning/evidence documents and governance files compete with the user's first task | Can make a small tool feel heavier than needed | Keep user documentation first and planning links secondary; do not add more process as a substitute for adoption |

High means important to resolve or explicitly accept before promotion. The packaging blocker
requires a fix and fresh artifact verification before treating a build as releasable.
No application-runtime correctness defect was demonstrated by the focused probes; the
archive-selection defect is a real packaging/privacy-boundary issue. This does not prove
the absence of defects in other paths.

## Packaging blocker: reproducible finding and proposed correction

The documentation-review build completed, but direct archive inspection rejected its
contents: 225 of 374 source-archive members were under `local-artifacts/`, including
synthetic exported tests and extracted cache copies. Its wheel contained zero such members.
Both unpublished artifacts were moved into ignored local quarantine. No archive was
uploaded or released. This was an archive-path inspection, not proof that every included
file was free of sensitive values; no such sensitive-value clearance is claimed.

The source target in `pyproject.toml` uses broad `include` patterns such as `"tests/"`.
In a fresh isolated source copy with Git initialized, a synthetic marker at
`local-artifacts/private-probe/tests/do-not-ship.txt` was confirmed ignored by Git and
still appeared in a source build. Thus a clean Git status and a clean-runner build do not
by themselves protect this distribution boundary. No real secret is needed to reproduce it.

In that isolated copy only, replacing the source target's `include` key with `only-include`
while retaining the listed root paths excluded the marker. The project's tracked packaging
configuration is unchanged in this review branch. This is a concrete proposed fix, not a
claim that release artifacts are now safe.
[Hatch's official build documentation](https://hatch.pypa.io/latest/config/build/#explicit-selection)
explains explicit path selection and its directory-traversal boundary.

The next approved fix should:

1. Select source-distribution roots explicitly and retain all intended code, tests, docs,
   policy/license files and workflow/configuration files.
2. Add a regression check that builds with ignored synthetic local/cache/credential-like
   marker files present and rejects unintended archive paths. Check wheel and source archive,
   both expected content and forbidden content; do not rely only on required-file presence.
3. Rebuild from the actual working tree, inspect members, run clean installs and smoke/
   acceptance checks, and record new artifact hashes. Never reuse the quarantined archive.

The initial isolated failure produced 150 source members including the marker; explicit
paths produced 149 without it. These counts describe that controlled probe, not a universal
expected source-file count. Local reproduction scripts/results are ignored audit artifacts.

## Reasons a developer would keep using it

- The regression executes current code. The separate-directory probe demonstrated that
  the test catches a reintroduced application behavior rather than just inspecting a trace.
- No provider account, cloud deployment or UI daemon is required for core execution.
  CLI/library users can use their existing pytest/CI pipeline; the UI is optional.
- Strict matching, latched fixture failures and explicit incomplete/error outcomes reduce
  false reassurance. Approval and reproduced-baseline checks are meaningful workflow controls.
- The native example keeps production graph construction independent of Fail2Test when
  dependencies are already injectable. Core install does not require the framework extra.
- Apache-2.0 software licensing, typed source, tests, locked development tooling and clear
  support/contribution policies give a reasonable foundation for adoption and contributions.

The costs are also real: authors must understand the case format, decide business rules,
prepare complete evidence, maintain fixtures and review content changes. For one simple
incident, hand-written pytest/mocks may have lower overhead. The added review/artifact
workflow needs to repay its complexity across maintained regressions.

## Alternatives and positioning checked against current primary sources

The following is a narrow capability comparison, not an exhaustive ranking or proof that
competitors lack any other functionality. Sources were read on 27 October 2026.

| Existing choice | Documented capability | Implication for Fail2Test |
|---|---|---|
| Plain pytest and LangGraph tests | LangGraph documents testing whole graphs, nodes and partial stateful execution | Explain why reviewed incident bundles/baselines add value beyond a hand-written test; [official guide](https://docs.langchain.com/oss/python/langgraph/test) |
| LangSmith pytest integration | Defines datasets/evaluations in pytest and logs outputs/feedback to experiments | pytest integration alone is not a unique differentiator; focus on reviewed fixture regressions; [official guide](https://docs.langchain.com/langsmith/pytest) |
| Promptfoo Python assertions | Custom Python output assertions and test context are supported | Declarative rules alone do not establish a moat; show the complete failure-to-regression workflow; [official docs](https://www.promptfoo.dev/docs/configuration/expected-outputs/python/) |
| VCR.py / pytest-recording | Records supported HTTP interactions into cassettes and replays them without those HTTP calls | Capture/replay and offline execution are established patterns; differentiate application/tool invariants, review and regression artifacts; [official docs](https://vcrpy.readthedocs.io/en/latest/) |

My inference: a credible initial message is **“Turn a recorded agent tool failure into a
reviewed pytest regression that catches the bug in your current code.”** Avoid claiming
“any trace to a test,” “fully automatic,” “no integration,” “fixes prompts” or complete
agent safety. No current-user counts, conversion rates or demand estimates were measured.

## Attraction, sharing and retention

A short demonstration should show an understandable failure, the selected rule, a red
regression, one code fix and the same green pytest test. A second scenario such as a
read-only agent requesting deletion helps show that the product is not refund-specific.
Use synthetic evidence and actual output. A screenshot can show the UI, but a terminal
test/code diff is stronger proof of the promised developer outcome.

For discovery, keep the README outcome, fit limits, runnable commands, output and integration
link above internal project history. A real screenshot/demo, a stable reviewed install
command and appropriate repository topics can improve the first impression. These are
recommendations, not evidence that the project will go viral. Stars do not establish
repeated use; later watch whether developers integrate a second case and keep it in CI.

For contributor readiness, the license, policies, tests, issue forms and roadmap are present.
Good first contributions should be concrete and verifiable: one synthetic compatibility
reproducer, a guide correction or an accessibility fix. Do not advertise nonexistent labels,
maintainers, response SLAs or an independent moderation team. Leave unrelated Dependabot
changes out of this candidate until reviewed separately.

Commercialization can remain future context: shared incident-case review, evidence
management and CI integration may have value if teams repeatedly use the local core.
There is no demonstrated willingness to pay, and none is needed to finish this open source
release. Do not build accounts/billing or restrict core usefulness to manufacture a business.

## Before-publication decision

1. Fix the demonstrated packaging blocker and verify rebuilt archives and installed workflows.
2. Review the documentation fixes and address privacy-safe diagnostics, or explicitly accept
   the remaining authoring friction. Keep the narrow supported scope visible.
3. Obtain an independent existing-application trial if feasible. Otherwise document owner
   acceptance of the usability uncertainty; do not turn a synthetic test into human evidence.
4. Finish final source/privacy/dependency review, candidate version/build checks and demo
   assets. Revalidate changes; do not treat the old green SHA as evidence for new runtime code.
5. Obtain explicit approval for public visibility, then apply/verify supported public branch
   protection, security reporting and community settings. Tags/releases/PyPI are separate choices.

An automatic recorder/vendor importer could have the largest longer-term effect on evidence
preparation friction, but it expands execution/privacy contracts and needs its own design
and approval. It is not silently included in this documentation step or promised for launch.

## Verification of this review's documentation changes

- The additional application probe completed 21 checks with expected exits, including core
  wheel import origin, demo use, a different forbidden-tool regression, in-place code fix,
  complete-project relocation, invalid evidence and stale review rejection.
- All eight commands in the new evidence guide matched expected exit codes. The actual JSON
  fenced blocks were parsed and imported; the same configured application failed before the
  fix and passed afterward, including generated pytest.
- Strict MkDocs, root/community/user-guide links and issue-form checks passed. Six existing
  publication-gate tests, Ruff lint and formatting passed. Remaining publication-gate facts
  are contacts, private reporting, broader host checks and owner acceptance; they stay false.
- Wheel/source build commands completed, but archive-content verification failed as described
  above. This is **not** a passing package-readiness result. The isolated proposed correction
  excludes the synthetic marker, but the actual package still needs the approved fix.
- These are focused review checks. No new full runtime-suite result, independent human
  usability measurement or successful hosted run for this unpushed documentation branch is claimed.
