# Implementation status

Updated 26 October 2026. This is a local development checkpoint toward one complete public release, not an early public release.

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
Ubuntu WSL2 on Python 3.12–3.14, 188 full Windows/Chromium tests at 88% coverage, 182 selected
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
- Verify hosted CI and any additional OS/browser/ARM claims; the documented local matrix is
  complete, not a promise about every dependency/version combination. Complete the final
  adversarial/privacy/security review before launch.
- Confirm public maintainer identities and working security/conduct contacts, then verify live
  GitHub private reporting and rendered templates. Local policies deliberately record these gaps.
- Complete benchmark methodology and final release/security review; refresh the prepared license
  inventory if dependencies change before publication.
- Configure and verify GitHub/registry identity and host-specific publishing checks only at the authorized publication step.

No GitHub remote, package publication, hosted executor, billing, account management or paid pilot is part of this checkpoint.
