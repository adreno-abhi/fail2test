# Optional AI suggestions verification

26 October 2026. Owner approved provider-independent suggestions and live free-only
OpenRouter checks with their existing key. Local model installation/start requires a separate
choice. This record distinguishes automated evidence from live inference and quality review.

## Implemented

Trusted TOML profiles choose OpenRouter, already-running loopback models or compatible HTTPS
chat endpoints without vendor SDKs. CLI `ai-preview` / `ai-propose` and the browser review
panel expose exact sanitized requests, explicit consent and digest checks. Generated Rule/Case
data is locally validated and remains unapproved. There is no application-code generation,
automatic review, provider retry, paid fallback or local model download.

Keys are read at send from environment or an owner-selected local file; they do not enter
the browser, preview, case, proposal, error output or repository. The owner's credential file
was outside this dedicated repo and untracked in the parent repo; a local parent Git exclude
was added for that filename. The credential value was never printed or copied into the repo.

Free-only OpenRouter profiles restrict model IDs, send zero maximum prompt/completion prices
and disable provider fallback. Default routing requests `data_collection=deny`; synthetic live
diagnostics also explicitly tested `allow` in an ignored local profile, without changing account
settings. Other hosted providers require explicit pricing acknowledgment through their profile
and preview. Local profiles connect only; no runtime has been installed or started.

## Automated evidence

The full suite passed **182 tests**, 88% combined statement/branch coverage, including
dedicated HTTP 400/404 and data-policy classifications. Real Chromium checks exercise preview with no send,
consent, background suggestions, apply-to-draft, save and renewed review. The browser sends
only to the local server; provider credentials remain server-side.

Transport tests use actual loopback HTTP stubs, including redirects, auth/credit/rate errors,
oversized responses and safe diagnostics. Proposal tests cover refusal/truncation/tool calls,
unsupported expressions, malformed/duplicate JSON, consent, staleness, payload limits and
unchanged saved-case/review state. Broken optional AI config preserves the key-free UI.
Clean wheel/source installs serve UI assets and create an AI preview without a key or SDK.

## Live OpenRouter evidence

Only the maintained public synthetic refund example was used. Owner approval covered these
requests. No private trace, repository source or credential was placed in prompt content.

1. The initial expected env file was absent; the first CLI attempt stopped with `AI_KEY_MISSING`
   before contacting a provider. The owner supplied the actual file path, which was used as-is.
2. `openrouter/free` returned HTTP 429. Account metadata subsequently reported a free-tier key,
   **0 of 50 daily free requests used, 50 remaining** at the time checked.
3. A pinned GPT-OSS free ID returned unavailable. Although its public page existed, it was
   absent from the live `/api/v1/models` catalog. Documentation pages alone are not availability proof.
4. The live catalog listed `nvidia/nemotron-3-super-120b-a12b:free` at zero input/output prices
   with structured-output support. Its request returned HTTP 404. A bounded diagnostic confirmed
   the no-endpoint/data-policy error, without printing raw provider errors or credentials.
5. Explicitly allowing data collection for that public synthetic request still returned no
   eligible endpoint. The owner chose read-only account privacy review. No account setting was
   changed; prompt publication remained disabled. A current different free model was selected.
6. `recursive/flint-v1.0:free` responded, but an initial 2048-token proposal did not pass the
   response/rule checks. It was rejected without changing the saved case. The exact cause of
   that first rejection was not recorded, so truncation is not claimed as established fact.
7. An explicit new preview with `max_tokens=4096` and data collection allowed for the public
   synthetic example returned a complete, locally valid two-rule proposal. API metadata reported
   **cost 0** and `finish_reason=stop`. Free-only guards remained enabled throughout.
8. Fresh execution showed the proposed refund-count rule failed on broken code and passed on
   fixed code. The extra output rule confused a tool response with application output and failed
   even on fixed code. Its own notes flagged uncertainty. Developer review rejected that extra
   assertion because it was unsupported by the stated requirement/application output contract;
   the primary model-proposed rule was preserved unchanged. This was not an automatic rule filter.
9. After renewed review of the primary rule, the broken baseline reproduced, the fixed runner
   passed, and the exported pytest test passed (**1 passed**). The original model proposal and
   separately reviewed rules remain distinct ignored local artifacts.

**Live end-to-end verification passed after explicit developer review.** This is one synthetic
example, not evidence that every model reliably proposes correct assertions. The additional
incorrect rule demonstrates why schema validity and a reproduced failure alone are insufficient.
The general prompt was tightened to distinguish tool responses from application outputs and
avoid unsupported output assertions; no claim is made that wording guarantees model correctness.
Paid endpoints were not selected, no credits were bought, no account policies were changed, and
no local runtime/model was installed or started. The zero cost is provider-reported metadata.

The shipped profile continues to request data collection denial by default. The synthetic live
profile's explicit `allow` does not authorize sending private evidence under that policy.

## Final checks

- Full suite: 182 passed, 88% combined coverage; targeted suggestion/HTTP/browser suite: 62 passed.
- Ruff lint/formatting, strict mypy (20 source files), strict MkDocs and Git whitespace checks: PASS.
- Wheel/source build and isolated core/native workflow checks: PASS, including installed AI
  preview without a key, vendor SDK or provider request. Package smoke checks are separate
  from the authorized live-provider check above.
- Chromium screenshot `output/playwright/ai-suggestions-desktop.png` visually reviewed.
- All run artifacts, environments and credentials are excluded from the dedicated repository.

## Environment and remaining scope

Windows / CPython 3.13.5, locked dependencies, Playwright 1.64.1 Chromium. Native examples and
the key-free workflow remain verified. Other providers/models/OS combinations require their
own conformance and quality evidence. Socket timeouts and byte/token caps bound ordinary
transport behavior; the server is not intended for hostile providers or internet hosting.

See the [user guide](../site/ai-suggestions.md) and [three-stage build contract](../planning/AI_SUGGESTIONS_BUILD.md).
This checkpoint authorizes no next feature, account-policy change, local-runtime setup or publication.
