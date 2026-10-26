# Fail2Test: OSS reference research

Checked **26 October 2026**. This file records primary-source facts and practical recommendations, not implementation or a claim of feature parity with mature projects. Other planning documents are maintained separately.

## 1. Mature project practices worth adopting

| Reference | Observed pattern | Recommendation for Fail2Test |
|---|---|---|
| [pytest repository](https://github.com/pytest-dev/pytest) | Separates source, tests, documentation, changelog fragments, scripts and CI configuration | Use `src/fail2test/`, `tests/`, `docs/`, `examples/`, `schemas/`, `changelog.d/`, `.github/`; add directories only with real content |
| [pytest contribution guide](https://raw.githubusercontent.com/pytest-dev/pytest/main/CONTRIBUTING.rst) | Documents development setup, targeted tests, changelog fragments, contribution expectations and black-box testing with `pytester` | Make a clean-clone contributor workflow reproducible; exercise generated tests in real pytest subprocesses; require contributors to understand and verify submitted code, including AI-assisted work |
| [Promptfoo contribution guide](https://www.promptfoo.dev/docs/contributing/) | Public contribution entry point with project structure and development workflow | Explain where adapters/assertions/exporters belong; provide one genuinely small contribution task and a complete local validation command |
| [Langfuse contribution guide](https://raw.githubusercontent.com/langfuse/langfuse/main/CONTRIBUTING.md) | Extensive setup and generated API-spec consistency checks; MIT core with exceptions in `ee`; CLA acceptance | Adopt machine-checked schema/example consistency. Do not copy a mature monorepo, enterprise folders or CLA mechanically; choose them to serve this project's actual model |
| [pytest integration guidance](https://docs.pytest.org/en/stable/explanation/goodpractices.html) | Explains test layout/import behavior and package integration | Test installed wheel/sdist rather than relying only on editable source imports; document the supported pytest import/setup model |

**Minimum public project surface:** README with tested quickstart and limitations; CONTRIBUTING; CODE_OF_CONDUCT with a real reporting channel; SECURITY with private reporting instructions; governance and maintainer decision rules; support/version policy; license and dependency notices; changelog; public milestone roadmap; issue/PR templates. A document should not promise staffed response times, governance members, audits, production readiness or compatibility the project does not yet have.

**Documentation design recommendation:** keep tutorials, task-based how-tos, conceptual explanations and API/schema reference distinct. Test all quickstarts using synthetic fixtures and no paid credentials. Publish exact compatibility claims and example outputs. Clearly label proposal versus accepted assertion, recording versus execution, and verified behavior versus untested hypothesis.

## 2. License recommendation and contribution rights

The authoritative [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) grants copyright and a defined contributor patent license, with patent-litigation termination conditions. Redistribution requires license/notices retention and modified-file notices, with NOTICE obligations when applicable; trademarks are not granted. Its contribution clause generally applies the same license to intentionally submitted contributions absent another agreement. The [MIT text](https://opensource.org/license/mit) permits modification, sublicensing and sale subject to notice retention; it lacks Apache's separate explicit patent grant/termination clause. Both permit commercial use and proprietary downstream work under their conditions.

**Recommendation:** Apache-2.0 for the runtime, CLI, schemas and adapters is a reasonable enterprise-friendly default. Use the exact unmodified license text, identify the actual copyright holder before publishing, and retain third-party notices. Decide the license of copied/generated test templates explicitly. State that users retain their trace/input rights; the software license does not automatically relicense their private data. This is a proposed project choice, not legal clearance of every dependency or output.

The [Developer Certificate of Origin 1.1](https://developercertificate.org/) certifies a contributor's right to submit work under the indicated license and acknowledges the public record. Sign-off is not copyright assignment and does not grant a maintainer unrestricted power to relicense everybody's contributions. [ASF contribution agreements](https://www.apache.org/licenses/contributor-agreements.html) illustrate that CLAs are a separate agreement choice; they are not required merely because a project uses Apache-2.0.

**Recommendation:** start with inbound=outbound Apache-2.0 plus DCO sign-off, preserving sign-offs through the chosen merge workflow. Do not promise a later proprietary dual-license conversion without obtaining the necessary rights. Hosted execution, collaboration, access controls, private retention and support can be commercial without relicensing the OSS core. If a CLA is desired for a concrete business reason, explain its rights plainly and adopt it before accepting contributions under different expectations. Do not retrofit an undisclosed relicensing plan.

## 3. Publishing, provenance and CI permissions

The [PyPI Trusted Publishing guide](https://docs.pypi.org/trusted-publishers/using-a-publisher/) documents OIDC publishing without a long-lived PyPI API token. It requires `id-token: write`, strongly recommends granting it at job scope, and encourages a GitHub environment. Configure the exact repository/workflow/environment identity on PyPI; use separate build/test and publish jobs. The [attestation guide](https://docs.pypi.org/attestations/producing-attestations/) says the official PyPA publishing action automatically generates/uploads attestations by default under supported Trusted Publishing.

**Recommendation:** default CI to `contents: read`; no publishing identity, secrets or write permissions in untrusted PR execution. Build artifacts once from the reviewed release commit, verify them, then publish those exact bytes through a protected `pypi` environment. Inspect the account's available environment protection features instead of assuming every reviewer rule is available on every plan. Publish wheel+sdist; test installation; attach hashes and artifact provenance. Verify provenance is actually visible on the uploaded files. Provenance establishes origin, not functional correctness or absence of malware.

Current [GitHub secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use) recommends workflow dependency lockfiles where supported, with full commit-SHA action pins as a fallback. It also emphasizes minimal token permissions and auditing third-party workflow code. Validate current lockfile support for the repository; otherwise pin every external action to a verified full SHA and use dependency update tooling. Do not copy mutable action tags from examples into a final release workflow without making this choice explicit.

[GitHub immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases) protect associated tags and assets after publication and create a release attestation. [Enablement instructions](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/prevent-release-changes) clarify that settings affect future releases. Create a draft, upload all intended assets, verify commit/tag and bytes, then publish. Titles, notes and certain release metadata remain editable. Fix a bad published artifact through a new version rather than replacing bytes. PyPI and GitHub attestations are distinct distribution records; verify both if distributing on both channels.

**Additional project-specific risk:** capture files, proposed assertions, generated Python and imported application entry points are untrusted inputs. Import/replay/test execution can run arbitrary application code. A Python virtualenv, subprocess or network-mocking library alone is not an OS sandbox. Keep offline parsing/inspection separate from explicit execution; run generated tests in an isolated runner without production credentials and validate any stronger container boundary separately. Never execute fork PR code through a privileged `pull_request_target` workflow.

## 4. First framework and current LangGraph semantics

[LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) distinguishes per-thread checkpointers from long-term stores. Current examples use `InMemorySaver`, `builder.compile(checkpointer=...)`, and `configurable.thread_id`. [Time-travel guidance](https://docs.langchain.com/oss/python/langgraph/use-time-travel) shows `graph.get_state_history(config)`, `graph.invoke(None, checkpoint.config)`, and `graph.update_state(checkpoint.config, values=...)` followed by `invoke(None, fork_config)`.

Replay re-executes nodes after a checkpoint, including model calls, API requests and interrupts; earlier nodes use saved results. `update_state` creates a branch rather than rolling the original thread back. Checkpoint history is not a snapshot of external databases, APIs, files or every application global. Reducers and node attribution affect state updates. Thus LangGraph support does not automatically provide deterministic, side-effect-free reproduction.

**Recommendation:** LangGraph is a plausible first adapter because public checkpoint APIs exist and tool-using graph failures are concrete. Restrict the first supported topology and versions in a published matrix. Require an application-owned test entry point and explicitly registered tool/model fixture seams; reject unsupported replay rather than silently calling live tools. Save version/environment metadata, redaction policy and fixture completeness. Keep framework-independent failure/assertion schemas and pytest export in the core.

Separate three modes in both architecture and docs: (1) inspect a recorded trace, (2) replay recorded responses to test application orchestration, (3) evaluate a changed model live. Replaying an unchanged recorded bad model response does not prove a prompt fix works. Live calls need their own budget, credentials and evaluation semantics, and should be optional after the offline product works.

## 5. Name and adjacent competition check

On 26 October 2026, a direct request to [PyPI's `fail2test` JSON endpoint](https://pypi.org/pypi/fail2test/json) returned HTTP 404; [GitHub's repository name search API](https://api.github.com/search/repositories?q=fail2test+in:name) returned `total_count: 0`. These observations do not reserve a name or clear a trademark/domain. PyPI's [name guidance](https://docs.pypi.org/project-management/choosing-a-name/) explicitly warns that an absent project can still have an unavailable name. Recheck before publishing; package registration is the authoritative availability test at that time.

Adjacent competitor [FailGate on PyPI](https://pypi.org/project/failgate/) currently describes generating sealed failing pytest tests from bug reports and grading proposed fixes. Treat its benchmarks as maintainer-reported claims. This makes 'generate a failing test for a bug' insufficient differentiation. Fail2Test's narrower position should be trace-derived agent behavior, explicit intended assertions, portable reviewed fixtures and verifiable bounded replay. Name availability does not establish novelty.

## Suggested gates for the plan

1. **Design:** reviewed trace schema, safety boundaries, assertion approval semantics, adapter coverage and example failing/fixed pair.
2. **Contributor preview:** clean-clone quickstart, deterministic no-credential examples, installed-artifact tests, issue templates and honest compatibility matrix.
3. **Public alpha:** real adopter validation, unsupported-case diagnostics, sensitive-data handling tests, signed-off contributions, release provenance and transparent known limits.
4. **Commercial pilot:** demonstrated repeat use and measurable test/review savings before hosted fleet features. Preserve the ability to run/export ordinary tests locally.

These gates are recommendations, not a claim that writing policy files alone supplies mature-project reliability or community trust.
