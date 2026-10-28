# Implementation status

Updated 28 October 2026. This is private pre-release preparation toward one complete public
release. The GitHub repository exists privately; no public release or registry upload has shipped.

## Current launch checkpoint

Local 0.1.0 preparation on 28 October aligns package/runtime/lock versions and release notes;
see the [candidate record](release-0.1.0.md). Approved free GitHub dependency graph,
vulnerability/malware alerts and security-update PRs are enabled. All 82 locked third-party
name/version pairs are visible in the remote graph, and it reports no open vulnerability
alerts. No push of this local candidate, public transition or release has occurred.

28 October: packaging and safe case diagnostics are merged in `main`
`97994307fbc19edd2e61fed47f4edaff43046912` and passed
[CI run 40645352245](https://github.com/adreno-abhi/fail2test/actions/runs/40645352245):
all six platform/Python matrix jobs, 211 full-suite tests including Chromium at 89% runtime
coverage, archive guards, package smoke and installed CLI/browser/native acceptance.
See [safe diagnostics](safe-case-diagnostics.md) and the
[final security/release review](final-release-review.md). The fresh advisory query found no
known vulnerabilities across all 82 locked packages. This is dated engineering evidence,
not a guarantee of safety or permission to publish.

The final review identifies remaining candidate/version, human usability acceptance and
host/public reporting/protection checks. The dependency controls were off during that
inspection and have since been enabled in the approved candidate-preparation step above.
The publication gate remains closed. Older verification records below retain their own
source/date scope. No public visibility, tag/release or registry upload has occurred.

## Implemented

- Installable Python package, project-local environment and committed dependency lock.
- Framework-independent strict case/rule/result models and JCS content identities.
- Neutral serial JSON import, known-sensitive-field sanitization and draft manifests.
- Deterministic rule proposals, explicit review and digest invalidation after edits.
- Baseline reproduction and fresh current-code execution in a managed subprocess.
- Strict model/tool matching, repeatable mock semantics and latched transport errors.
- Five rule kinds; complete/pass, complete/fail and incomplete/error result distinctions.
- Baseline-bound pytest export with readable code and portable reviewed fixtures.
- Input-deletion reduction with execution/time budgets and renewed-review requirement.
- Packaged key-free refund example and CLI init command.
- Focused LangGraph graph-factory helper; native graph broken/fixed conformance test.
- Native BaseChatModel/tool fixture replacements, serialized ToolNode support and native message-state serialization.
- Existing-style native graph example whose constructor is independent of Fail2Test.
- Current quickstart, integration/safety docs and strict local docs build.
- Bundled local browser UI for evidence/upload, key-free proposals, review/editing, supervised jobs, reduction comparison and export preview/save.
- Session/origin/Host enforcement, contained filesystem operations, in-memory sanitized uploads and real Chromium acceptance tests.
- Optional OpenRouter/local/custom compatible suggestion profiles, exact sanitized request
  preview, explicit consent, server-side credentials and unapproved rules in CLI/UI.
- Root community policies, issue/PR forms, adapted Contributor Covenant, DCO, release checklist
  and locked third-party license metadata/file-hash inventory.

## Verification

The integration suite runs a generated pytest file against broken code, edits the application's implementation, and reruns the exact same test successfully. It also checks that missing fixtures, swallowed errors, unsupported async and malformed evidence do not become passes. Automated CLI tests exercise the full local import/review/validate/run/export workflow.

The initial [build verification record](build-verification.md) records the first 85-test checkpoint. The latest [native adapter verification](native-adapters-verification.md) records **120 passing tests**, 88% combined coverage, passing lint/types/docs, and fresh core/native wheel and source-distribution checks. Test counts are not a claim of production readiness or benchmark superiority.

The subsequent [local UI verification](local-ui-verification.md) records **148 passing tests**,
88% combined coverage, browser/HTTP acceptance and clean installed-asset checks. It is the
full-suite evidence for that earlier checkpoint.

The latest [AI suggestion verification](ai-suggestions-verification.md) records **182 passing
tests**, 88% coverage and a live free-model proposal reviewed through broken/fixed execution
and passing pytest export. It also documents an incorrect extra assertion rejected in review.

## Remaining before the agreed complete first release

The latest [compatibility/acceptance record](compatibility-acceptance.md) verifies Windows and
Ubuntu WSL2 on Python 3.12â€“3.14, 188 full Windows/Chromium tests at 88% coverage, 182 selected
tests per other matrix row, and 182 corrected lower-bound tests. Installed-wheel CLI/UI/native
trials reproduce broken/fixed behavior and preserve an unchanged exported test. Automated
timings are recorded separately from unmeasured human first-use effort.

[Local repository readiness](repository-readiness.md) records the completed community,
packaging and license-evidence work, six gate tests and the remaining publication prerequisites.

- Review the completed [local UI verification](local-ui-verification.md); broader browser/platform and formal accessibility auditing remain future checks.
- Observe a human first-use trial or obtain owner acceptance of the documented usability
  uncertainty. Broader message/tool support needs its own new acceptance evidence.
- Review [AI suggestion verification](ai-suggestions-verification.md), including live free-provider
  availability limits and the distinction between schema validity and proposal quality. The
  default workflow remains key-free and performs no provider requests.
- Broaden reduction beyond input deletion only if it preserves clear supported semantics.
- Hosted CI is verified for the documented Windows/Ubuntu matrix. Additional OS/browser/ARM
  claims need their own evidence; the matrix is not a promise about every dependency/version
  combination. The final maintainer security review is complete for the stated revision; recheck the exact release candidate.
- Confirm public maintainer identities and working security/conduct contacts, then verify live
  GitHub private reporting and rendered templates. Local policies deliberately record these gaps.
- Finish exact-candidate release checks and owner acceptance; refresh the prepared license
  inventory if dependencies change. Human timing/benchmark claims remain unmeasured.
- Configure and verify GitHub/registry identity and host-specific publishing checks only at the authorized publication step.

The GitHub remote and private source/CI setup are complete. Package publication, a hosted
executor, billing, account management and paid pilots remain outside this checkpoint.
