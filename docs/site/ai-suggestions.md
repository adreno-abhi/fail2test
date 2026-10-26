# Optional AI-assisted suggestions

Fail2Test can ask a user-selected model to propose its existing declarative rules. The model
does not execute your application, create Python assertions, approve a case or establish a
baseline. Every result requires developer review. The deterministic `propose` command and
the normal fixture workflow need no provider configuration, credentials or network.

## Provider profiles

Put profiles in the same **trusted** TOML file as your runners. Evidence cannot select or
modify these settings. The initialized example includes this optional free-only profile:

```toml
[suggestions.profiles.openrouter-free]
kind = "openrouter"
base_url = "https://openrouter.ai/api/v1"
model = "openrouter/free"
api_key_env = "OPENROUTER_API_KEY"
free_only = true
response_format = "json_object"
```

You can pin a currently available `:free` model ID instead. `openrouter/free` chooses among
free models, so record the returned `actual_model` when evaluating quality. Free availability,
quotas and provider policies can change; failures do not trigger a paid fallback. Fail2Test
sends zero maximum prompt/completion pricing, disables provider fallbacks and uses no model
fallback list for free-only OpenRouter profiles. It never buys credits or changes accounts.
Use your provider's account controls too; Fail2Test's configuration is not a billing contract.

The default `allow_data_collection = false` requests providers whose declared data collection
policy is `deny`. This may reduce free capacity. Providers' retention/training terms still
apply. Setting `allow_data_collection = true` is an explicit configuration choice visible in
the preview; no code changes it automatically.

Your OpenRouter account's separate free-model privacy controls also apply. A per-request
`allow` does not override those account settings. `AI_DATA_POLICY_BLOCKED` means no eligible
endpoint matches those combined settings; review your account choices or stay with the
key-free route. Fail2Test does not automatically relax privacy to obtain a result.

For an **already running** local server, no provider key is needed:

```toml
[suggestions.profiles.local]
kind = "local"
base_url = "http://127.0.0.1:11434/v1"
model = "your-installed-model-name"
response_format = "json_object"
```

Use the endpoint/model of your own Ollama, LM Studio, llama.cpp or another compatible server.
Local profiles accept only loopback HTTP/HTTPS. Fail2Test does not install/start a runtime or
download/load models. Protocol support alone is not evidence a particular model is suitable.

For another OpenAI-compatible hosted service:

```toml
[suggestions.profiles.my-provider]
kind = "compatible"
base_url = "https://your-provider.example/v1"
model = "your-model-id"
api_key_env = "MY_PROVIDER_API_KEY"
free_only = false
response_format = "json_object"
```

Custom hosted endpoints require HTTPS, a key-variable name and an explicit `free_only=false`:
Fail2Test cannot verify their prices. This does not mean they must charge; it means the
OpenRouter zero-price guard is unavailable for them. Never embed credentials in a URL.
OpenRouter itself must use `kind="openrouter"`, including when supplied through a custom profile.

Supported transport: non-streaming `POST BASE_URL/chat/completions` returning
`choices[0].message.content` as a JSON string with `finish_reason="stop"`. This is the
OpenAI-compatible chat protocol, not a dependency on OpenAI's service or SDK. Native APIs
using different schemas need another adapter and are not currently supported.

`response_format` may be `json_object` (default), `json_schema` or `text`. JSON Schema support
and accepted keywords differ by provider; local validation is always enforced. Unsupported
formats fail with a safe provider error rather than triggering a hidden retry. Defaults:
`max_tokens=2048` (256–8192), `timeout_seconds=30` (positive, at most 30). The transport uses
a socket timeout, a 64 KiB request cap and a 1 MiB response cap. Redirects and environment
proxies are disabled; direct access to the configured endpoint is required.

Reasoning models may need a larger output budget before producing the JSON answer. The
synthetic live check used `recursive/flint-v1.0:free` with `max_tokens=4096` and explicit data
collection permission for public synthetic evidence. Availability and quality are not guaranteed;
see the verification record in the repository. A schema-valid extra rule was rejected during
review because it assumed an application output shape from a tool response.

## Credentials

Supply the named variable in the server/CLI process environment, or an ignored local env file
containing a `VARIABLE=value` assignment. Quoted single-line values and UTF-8 BOM are supported.
Never put keys in TOML, cases, proposal artifacts or Git. Env files are read only at send;
preview does not need a key. Environment variables take precedence over the selected file.

The browser server defaults to `WORKSPACE/.env.local`. Select another owner-controlled file:

```text
uv run fail2test ui --workspace local-artifacts/demo --env-file .env.local
```

The file path is chosen when starting the trusted server; browser requests cannot change it.
Credentials never appear in browser fields or API responses. The CLI requires `--env-file`
when reading a file rather than the process environment.

## Browser workflow

1. Import/open a case and go to **Review → Optional AI-assisted suggestions**.
2. Choose a configured profile and describe intended behavior. Unsaved case edits must be
   saved first. Historical behavior alone is not a business requirement.
3. **Preview AI request**. Inspect the exact sanitized chat body, endpoint, model, free-only
   policy and data-collection setting. It includes the case title, input, fixtures, existing
   rules, your intended behavior and the allowed output schema. It excludes raw original
   traces, source-reference paths, application source and arbitrary repository files.
4. Acknowledge this payload/destination and **Send previewed AI request**. A background job
   keeps the UI responsive and prevents simultaneous workspace mutations.
5. Inspect returned rules and uncertainty notes, then **Apply suggestions to draft** if useful.
   This replaces draft rules only. Save validates the case and clears any earlier review and
   baseline. Explicitly approve it and reproduce the selected failure as usual.

Changing evidence, requirement or configuration invalidates the preview. Known sensitive
fields are sanitized before transmission, but detection is best effort: inspect the actual
payload. A local profile sends to your configured loopback server, which remains trusted
software and could have its own networking behavior.

## CLI workflow

```text
uv run fail2test ai-preview local-artifacts/demo/case --config local-artifacts/demo/fail2test.toml --profile openrouter-free --requirement "At most one refund per order; require a refund." --out local-artifacts/demo/ai-preview.json
uv run fail2test ai-propose local-artifacts/demo/case --config local-artifacts/demo/fail2test.toml --preview local-artifacts/demo/ai-preview.json --env-file .env.local --allow-send --out local-artifacts/demo/ai-rules.json
```

Read the preview file before the second command. `--allow-send` is explicit authorization;
without it nothing is sent. The request is reconstructed from current trusted configuration
and case data and must match the preview digest. Edited previews cannot redirect a request.
Credential-source selection and timeout use that same validated settings snapshot, so a
concurrent profile edit cannot substitute another profile's credential after the check.
Inspect/edit `ai-rules.json`, then use the existing `review --rules` workflow. Its content
identity and provenance metadata are review aids, not proof that the suggestions are correct.

## Errors and quality

Authentication, unavailable free capacity/credits, rate limits, unreachable endpoints, refusal,
truncation, tool-call responses, malformed JSON and invalid/duplicate rules leave the case
unchanged. Raw provider errors are not exposed. There are no automatic retries or model
switches, and no silent switch to a local runtime. Ask for a new proposal explicitly or use
the key-free route. Error codes include `AI_KEY_MISSING`, `AI_RATE_LIMITED`,
`AI_CREDITS_REQUIRED`, `STALE_AI_PREVIEW`, `AI_PAYLOAD_TOO_LARGE` and `INVALID_AI_PROPOSAL`.
`AI_MODEL_UNAVAILABLE` identifies a missing/unavailable endpoint; `AI_REQUEST_UNSUPPORTED`
identifies an unsupported request. `AI_DATA_POLICY_BLOCKED` identifies OpenRouter's explicit
no-endpoint/data-policy error without showing the raw provider message.

Use synthetic evidence to evaluate whether suggestions express the intended requirement and
distinguish broken/fixed code. Schema validity alone is not semantic correctness. Automated
tests use deterministic mock providers and real local HTTP stubs without model downloads;
live provider checks are optional, separately authorized and recorded separately.
