# Future commercial context — deferred

**Current direction:** this document preserves future options only. No commercial feature, pricing experiment, sales activity, paid pilot, cloud service or enterprise program is part of the initial local end-to-end build. Complete and publish the useful open source product first. Any execution of the future steps below requires a later scope decision.

## Model

Build a useful Apache-2.0 local project first. Commercial readiness means maintaining stable portable artifacts, clear ownership, dependency/license hygiene, measurable execution and deployment seams. It does not mean building billing, multitenancy, SSO or a cloud scheduler into v0.1.

## OSS commitment

Keep local import, sanitization, reviewed rule creation, fixture execution, supported adapters, reduction, pytest export, schema documentation and self-hosted usage useful under the published license. Do not require an account for the local path. Never encrypt or withhold a user's regression fixtures to force cloud adoption. Avoid artificial test-count limits in the OSS runtime.

New proprietary organizational modules, if later introduced, must have an explicit license and dependency separation. Apache-licensed core remains Apache-licensed. A hosted service may use the core commercially, including by other organizations; this is part of the selected model. Do not promise exclusive hosting rights or unilateral relicensing of external contributions.

## Paid value candidates

| Offering | Buyer | Value beyond local execution | Needed proof |
|---|---|---|---|
| Managed regression runs | AI engineering team | Scheduling, managed compute, retained result history and failure notifications | Repeated local use and willingness to delegate execution |
| Shared incident-to-test workflow | Engineering lead | Reviewed case library, assignment, organizational approvals and provenance | Multiple users coordinate real failure fixes |
| Model/prompt comparison | Reliability owner | Budgeted live-model batches with mocked tools and comparison reports | Sampling methodology improves a real upgrade decision |
| Customer-managed runners | Security-sensitive engineering org | Control-plane orchestration while execution remains in customer environment | Actual data/security requirement and deployment maintenance capacity |
| Enterprise deployment/support | Platform team | Private deployment, identity integration, operational help and support commitments | Budget owner, repeat workload and support economics |

No feature is assumed validated solely because an adjacent vendor offers it. Test whether users need Fail2Test in addition to Langfuse/LangSmith and whether it is a product or an integration they expect their existing platform to provide.

## Product seams to preserve now

- Case and result schemas independent of accounts, billing and deployment.
- Explicit runner identity/capabilities and structured errors.
- Deterministic fixture execution separate from paid inference and hosted scheduling.
- Clear model/tool dependency injection without hard-coded cloud clients.
- Exportable case bundles and redacted reports; no proprietary-only case format.
- License/provenance on every redistributed example or benchmark artifact.
- Stable public interfaces with compatibility/deprecation policy.

Do not add tenant IDs to every local class, define empty billing interfaces, or introduce event buses “for later.” A future control plane can consume the supported case/result contracts and use a separate execution authorization model.

## Validation sequence

1. Recruit five engineers with real failures. Verify runner integration and reviewed test usefulness.
2. Seek three repeat users who retain and rerun a generated test on a later change.
3. Identify a budget owner and recurring pain: regression batch operations, sharing, upgrade evaluation or private deployment.
4. Offer two scoped paid pilots with written workload, data handling, deliverables, cost cap and success measures. Use customer-controlled execution initially where practical.
5. Review support, correction effort, infrastructure and model cost. Continue only if the workflow can be delivered reliably without unlimited founder intervention.
6. Design the hosted service only after those findings justify it; publish OSS/commercial boundaries before taking outside contributions to paid modules.

These are proposed decision gates, not claimed customer counts or market forecasts. No customer outreach or contracting has been performed by this plan.

## Pricing hypotheses

For interviews, test a capped team plan in roughly the USD 49–199/month range for managed regression workflow, with additional execution/model usage separately bounded. Treat this as an experiment, not a market-supported price. Enterprise/private deployment requires scoped cost and support analysis; no arbitrary annual contract promise.

Price for workload and coordination value, not just the number of generated assertions. A user with a dozen high-value tests may gain more than a user with thousands of low-value cases. Allow BYO credentials/customer-managed execution where justified, but never shift unclear spend to the customer silently.

Track contribution margin after compute, model usage, storage, support, onboarding and failed runs. Avoid unlimited live-model inference or arbitrary customer-code execution under a cheap flat plan. Publish visible run budgets and consumption before scheduling costly work.

## Cloud readiness gate

Before any shared executor exists, require a separate design for: authenticated tenant authorization, immutable artifact identities, isolated ephemeral execution, resource/egress limits, secrets injection and destruction, network policy, cancellation, rate limits, storage encryption, retention/deletion, audit history, backup/recovery, abuse prevention, incident response and operations ownership. Validate these controls with tests and deployment evidence. Do not claim SOC 2, regulated-data readiness, secure sandboxing or an SLA before those commitments have been established.

## Community trust and business governance

Publish which features are open, which are experimental and which are paid. Keep security fixes for supported OSS releases available through the normal process. Paid customers may fund work but cannot bypass review. Separate sponsor priority from maintainer authority. Contributors should know the license and commercial intent before contributing; the project should not solicit community work under misleading promises about future ownership.

## Defensibility

The durable advantage must be accurate and low-friction conversion of real agent failures into retained tests. Accumulate a permissioned corpus of useful synthetic failures, strong adapter conformance, reliable reduction, excellent docs and maintained integrations. A generic trace UI, a proprietary wrapper over pytest or raw user data collected without rights is not a defensible foundation.

References: [Langfuse commercial offers](https://langfuse.com/pricing), [LangSmith commercial offers](https://www.langchain.com/pricing), [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
