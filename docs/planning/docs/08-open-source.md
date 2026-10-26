# Open source licensing, contribution and governance

## Licensing decision

Recommend **Apache License 2.0** for the initial core, CLI, runtime, schemas, documentation and project-authored examples. It permits commercial use and contains an express contributor patent license with conditions and patent-litigation termination provisions. Follow the license's redistribution and notice requirements. This is a licensing recommendation for the project; it does not establish the rights to someone else's trace, dependency or contribution.

Use the exact official license text, not a generated paraphrase. The reference URL is [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt). Do not insert a fabricated company or assign contributors' copyrights to the founder. Identify actual initial copyright holders/years where appropriate. Use SPDX `Apache-2.0` metadata and consistent headers where needed.

`NOTICE` contains applicable project/third-party notices; it is not an invented list of dependencies or an extra restriction. Maintain third-party license inventory separately. If distributing another project's material, preserve the applicable license/NOTICE requirements. Project-created synthetic benchmark data can use Apache-2.0 for simplicity; any externally sourced dataset retains its own license and provenance and must be reviewed separately. No customer trace redistribution merely because it has been redacted.

Apache-2.0 enables an open ecosystem but does not prevent competitors from hosting the core. Hosted operations, integration quality, maintained test libraries with clear rights, reputation and support are commercial differentiators. Do not imply that a permissive license protects all monetization paths.

## Contributions: DCO, not assignment

Use Developer Certificate of Origin 1.1 sign-off (`git commit -s`) with a link to its exact [official text](https://developercertificate.org/). The contributor certifies the rights required to submit their work under the project license. They retain copyright. Start without a separate broad CLA or copyright assignment.

DCO is not a grant of unilateral relicensing rights. The founder cannot assume they can later convert all outside contributions into an incompatible proprietary edition. A future licensing change would need a rights/consent analysis. Existing permissively licensed releases continue to be usable under their released terms.

AI-assisted contributions are welcome under the same standard: the contributor understands the change, has rights to contribute, discloses material assistance where relevant to provenance/review, tests it, and signs off. Do not require disclosure of private prompts or secrets. Generated code is not exempt from license, correctness or security review.

## Governance at launch

Use an honest maintainer-led model. The founder/project steward sets product direction; named maintainers approve changes within their areas; a named release owner publishes; a named security contact coordinates private reports. Record actual handles and responsibilities in `MAINTAINERS.md`. No fictional foundation, steering committee, elections or bus-factor guarantees.

| Change | Decision process |
|---|---|
| Docs, examples, internal fix | Issue/PR and maintainer review |
| Behavior change within existing contract | PR with regression evidence, docs and changelog |
| Public interface/schema, privacy default, execution semantics | Public RFC, compatibility/security assessment and ADR |
| License/governance/trademark policy | Public proposal, rights review and documented steward/maintainer decision |
| Critical vulnerability | Private advisory process; public explanation after coordinated release |

RFCs state problem, users, alternatives, proposed contract, compatibility, security/data flow, migration, maintenance cost and acceptance evidence. Seek at least seven calendar days of public comment for nonurgent substantial changes; extend for difficult issues. Small bug fixes need not wait. Maintainers explain decisions and record dissent; no engagement quota can force unsafe changes.

## Contributor journey

1. Read the README, contribution guide, code of conduct and supported scope.
2. Choose a labeled issue or discuss a larger proposal before coding.
3. Set up the minimal dev environment and run the key-free example.
4. Add a failing behavioral case when fixing a defect; keep the patch focused.
5. Update docs/changelog and sign off commits.
6. Open a PR using the template, with reproduction/validation evidence and privacy considerations.
7. Receive a substantive review. Reviewer checks behavior, false-pass risks, compatibility and maintenance impact.
8. After merge, release notes credit contributions unless the contributor prefers otherwise.

Keep docs-only setup light. Offer one small issue with mentor notes per active area when capacity permits. Document how new adapter maintainers can add conformance evidence and support versions. Unmaintained adapters are marked experimental or deprecated rather than silently left in the supported list.

## Maintainer growth and sustainability

Recognize repeated helpful contributions in code, docs, issue triage, user support or security. Invite contributors to an area-maintainer role after demonstrated judgment, then add permissions incrementally. Release/security authority requires explicit onboarding, 2FA and recovery planning. Privileges can be removed for inactivity or misuse through a documented explanation and access-revocation process.

Publish realistic best-effort review targets; do not promise commercial response times to a volunteer community. Start with one weekly triage session and a monthly roadmap review. If capacity falls, mark the status and narrow scope. Security reports and code-of-conduct concerns need a private route distinct from ordinary support.

## Public roadmap and community surfaces

Publish `ROADMAP.md` from day one. Use GitHub milestones for release scope, linked issues for implementation, and Discussions for usage/design questions once enabled. A GitHub Project board is optional; avoid maintaining duplicate contradictory status systems. The roadmap is directional; only confirmed release notes describe shipped capabilities.

Start with GitHub Issues/Discussions and documentation. Add chat infrastructure only if someone can moderate and summarize important decisions back to GitHub. Public information must not depend on membership in a private Discord/Slack.

## Conduct, support, trademark and sponsorship

Adopt a recognized code of conduct with actual enforcement contacts before publication. Never publish a policy whose reporting address does not work. Support docs distinguish bugs, usage questions, private security reports, and paid support. Avoid aggressive stale-issue auto-closure in a young project; ask for missing evidence and explain closures.

Check brand/package availability before launch. A trademark policy can protect the identity without restricting licensed code use. Do not claim ownership of a registered mark or domain before it exists. Sponsorship and commercial affiliations are disclosed in public governance. Paid feature requests get transparent prioritization and do not buy a bypass of review or security policy.

## Publication checklist

- Exact LICENSE and applicable notices included in source and built distributions.
- Real maintainers and private reporting/enforcement contacts filled in.
- DCO requirement and sign-off correction instructions tested.
- Contributor guide, support policy, roadmap, issue forms and PR template available.
- License inventory and benchmark rights recorded.
- Ownership/permissions verified for GitHub and package publishing.
- README claims match tested capabilities; no fake badges, download counts, customers or benchmark results.

Primary references: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), [Apache licensing FAQ](https://www.apache.org/foundation/license-faq.html), [DCO](https://developercertificate.org/), [Open Source Definition](https://opensource.org/osd), [GitHub community profiles](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories).
