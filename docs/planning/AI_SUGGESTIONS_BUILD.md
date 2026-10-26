# Optional AI suggestions build contract

26 October 2026. Owner approved provider choice, OpenRouter free-only verification and reuse
of their existing OpenRouter key. A local model runtime must not be installed/started without
asking first. Scope: suggestions only; no model changes to fixture execution or publication.

## Stage 1 — direction: PASS

EXISTS: strict Rule/Case contracts, deterministic proposals, browser review and supervised jobs.
Use a small OpenAI-compatible chat HTTP transport, independent of any vendor SDK. Profiles
support OpenRouter, already-running local endpoints (Ollama/LM Studio/llama.cpp) and custom
compatible HTTPS endpoints. Native APIs with incompatible protocols need future adapters;
there is no claim that every provider implements this protocol identically.

Browser/CLI → sanitized request preview → explicit send → bounded provider response → local
Rule/Case validation → unapproved proposal → existing save/review/baseline workflow.
Case files cannot choose an endpoint, model, key name or credentials. No application code,
complete raw trace, source-reference paths or arbitrary repository files enter the request.

## Stage 2 — build contract: PASS

Trusted runner TOML adds `[suggestions.profiles.NAME]`: kind, base_url, model, api_key_env,
response_format, free_only, timeout_seconds and max_tokens. Local profiles allow loopback HTTP
only and need no key. Remote profiles require HTTPS; redirects and environmental proxies
are disabled. OpenRouter profiles use its fixed API origin; free-only accepts `:free` models
or `openrouter/free` and sends zero maximum prompt/completion prices, no model fallback list.
Optional non-OpenRouter paid endpoints require explicit profile configuration.

Preview returns exact sanitized chat body, destination/model, case/request digests and data
handling policy. Sending requires the matching digests and explicit acknowledgement. Source
content and provider output remain untrusted data, never executable expressions/Python.
Requests cap at 64 KiB; responses cap at 1 MiB; transport timeout caps at 30 seconds. No hidden
retry, repair request or automatic switch to another model/provider. Schema/refusal/empty/
truncated/network/auth/rate-limit errors retain safe codes and leave the case untouched.

Credentials come from an explicitly named process environment variable or owner-selected
local env file (default workspace `.env.local` for UI). Env files are read only at send,
bounded and never served or copied. Tokens are never browser fields, HTTP responses, reports,
request previews or error text. UI suggestions use the existing one-job lock. Applying a
validated result only edits the draft; saving clears review/baseline and requires approval.

Accept with mock HTTP/transport contract tests, adversarial model output, profile/cost/payload
guards, CLI preview/send and Chromium preview/send/apply flow. Live validation is synthetic
only, OpenRouter free-only with the owner's existing key. No local runtime/download allowed.

## Stage 3 — local operation: PASS

No new runtime dependency, service, database or model runtime is required. Configure a profile
in trusted TOML, provide its key outside Git, preview and explicitly request suggestions.
The deterministic proposal path remains unchanged if configuration/key/network is unavailable.
Stop using a profile to disable it; no case migration is needed. Maintain normal workspace
version control. Job reports are session-local and sanitized; no raw provider error logs.

Owner accepts use of free OpenRouter on synthetic evidence only. Provider availability and
free capacity are external dependencies, so functional mock coverage is separate from live
evidence. Unknown model quality cannot be a build-gate pass claim: evaluation is PARTIAL
until actual tests complete. Maintainer owns acceptance; Codex implements/verifies this step.

References: [OpenRouter API](https://openrouter.ai/docs/api_reference/overview),
[structured output](https://openrouter.ai/docs/guides/features/structured-outputs),
[free router](https://openrouter.ai/docs/guides/routing/routers/free-router),
[provider policies](https://openrouter.ai/docs/guides/privacy/provider-logging).
