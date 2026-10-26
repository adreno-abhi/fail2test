# Governance

Fail2Test is maintainer-led. Initially the project owner is the sole human maintainer.
AI tools assist development and do not hold maintainer authority, credentials, voting rights
or responsibility for release/security decisions. There is no foundation, steering committee
or independent enforcement team. Public identities and reporting contacts are tracked in
[MAINTAINERS.md](MAINTAINERS.md) and must be verified before publication.

## Decisions

The maintainer decides scope, merges, releases and support priorities using correctness,
user benefit, privacy and maintenance cost. Contributors may challenge a decision with
concrete requirements, alternatives and evidence. Keep disagreement respectful and focused.

Ordinary fixes use issues/PRs. Public APIs/schemas, execution semantics, privacy defaults,
major dependencies, licensing and substantial architecture changes need a short proposal
and recorded decision. Include the problem, options, compatibility/migration effect,
validation and rejected alternatives. Store durable decisions under `docs/decisions/` or link
the public discussion from a tracked document. Private security fixes may be discussed
privately until disclosure; record the public explanation when safe.

While local development continues, the owner's step-by-step approval process in [PLAN.md](PLAN.md)
controls scope. After publication, contributors can comment on proposals before the maintainer
decides. There is no guaranteed voting period or majority vote, and sponsorship does not buy
merge rights or override safety/review obligations. Update [ROADMAP.md](ROADMAP.md) when
priorities change; unchecked work is direction, not a delivery promise.

## Maintenance and access

Invite additional maintainers based on sustained useful work and judgment across code,
reviews, documentation, triage and conduct. Record responsibilities and agreement publicly.
Grant least-privilege access incrementally, require suitable account protection and document
release/recovery responsibilities before expanding publishing or security access.

Access can be reduced for inactivity, security risk or misuse. Explain decisions privately
when sensitive, publicly when appropriate, and preserve access recovery without sharing
personal credentials. There is currently no guaranteed succession plan; establishing a
backup maintainer is future work, not an existing capability.

Contributors retain copyright under the published licensing/contribution policy. Any future
commercial offering must have its own scope; it does not revoke rights already granted under
Apache-2.0 or imply that volunteer support is a paid service.

The project owner accepts releases. [PUBLISHING.md](PUBLISHING.md) controls the final
identity/contact, quality, repository and package checks. A local commit is not publication.
