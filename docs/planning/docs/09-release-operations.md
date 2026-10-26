# CI, distribution and operations

## Operational scope

**Current delivery policy:** finish the complete product locally, then perform owner-authorized GitHub/registry setup and host-specific checks at the publication step. No public early alpha/beta releases are planned. Test-registry metadata or a private host rehearsal must not be created before that step without authorization. A private host check, if necessary, precedes making the finished project public.

The alpha is a local Python package. There is no always-on backend, production database, login service or cloud deployment. Production for this release means trustworthy distributions and a documented local/CI execution workflow. Hosted-service operations require a separate design and readiness gate.

## Environment matrix

| Environment | Purpose | Credentials / data | Execution |
|---|---|---|---|
| Contributor laptop | Develop and run examples | Synthetic fixtures; no provider credentials needed | Local supported Python |
| Fork PR CI | Verify contributions | No repository secrets or production evidence | Ephemeral hosted jobs, restricted token |
| Main-branch CI | Full core/docs/package checks | Synthetic fixtures only | Supported matrix |
| Compatibility job | Dependency/adapter bounds | Synthetic fixtures; no provider keys | Scheduled or manual, bounded |
| TestPyPI rehearsal | Verify publishing/install path | OIDC publisher identity, protected environment | Built artifact from reviewed source |
| PyPI release | Distribute reviewed package | Registry owner plus configured trusted publisher | Protected release job |
| Future live-model evaluation | Opt-in proposal/eval validation | Dedicated capped project credentials, sanitized data | Separate protected workflow; absent at alpha |

## Required workflows

### `ci.yml`

Checkout, install pinned development tooling, sync locked development dependencies, lint/format/type checks, offline tests, package build and artifact-install smoke. Default token permissions are read-only. Matrix is lean enough to remain contributor-friendly. Do not share privileged caches or secrets with untrusted jobs. Never check out/run untrusted PR code in a privileged `pull_request_target` workflow.

### `docs.yml`

Strict build, local link checks and executable tutorial/reference examples. External link checks are bounded/scheduled to avoid transient website failures blocking ordinary PRs. Deployment to docs hosting uses a distinct least-privilege job and protected main-branch source.

### `compatibility.yml`

Documented minimum/recent dependency combinations, LangGraph versions, supported OS/Python cases and dependency-update candidates. Results update a maintained support matrix. Optional integrations do not expand the core install or require secrets for fork PRs.

### `release.yml`

Build the wheel and sdist from reviewed tagged source once; verify metadata, licenses, schemas and quickstart from those artifacts; produce checksums/SBOM; rehearse TestPyPI; promote the same verified distributions through a protected PyPI publishing job. Rebuilding for promotion must be avoided or reproducibility explicitly checked. TestPyPI dependency installation instructions must account for unavailable upstream packages without teaching unsafe mixed-index dependency resolution.

Use PyPI trusted publishing/OIDC rather than a long-lived registry token where supported. Grant `id-token: write` only to the publishing job and restrict publisher workflow/environment identity. Use attestations supported by the publishing action. Configure protected environments with the actual owner and recovery procedures; never assume an OIDC claim alone is authorization.

### Dependency and workflow protection

Use supported workflow dependency lockfiles where available and verified; otherwise pin third-party Actions to full commit SHAs and have update tooling maintain them. Review workflow, lockfile, signing and publishing changes with elevated care. Set job/concurrency timeouts. Ensure no forks or arbitrary branches can call a privileged release path with attacker-controlled artifacts.

## Version and support policy

- Use PEP 440-compatible versions and a published semantic compatibility policy. Select the complete initial version at readiness (for example 0.1.0); no staged public prerelease sequence is required.
- Before 1.0, breaking changes still require release notes, migration guidance and an explicit version increment. Do not treat `0.x` as permission to silently break fixtures.
- Package version, case schema version, result schema version and adapter capability version are distinct.
- Alpha supports the latest alpha release. Stable support duration is decided and published before 1.0 based on maintenance capacity.
- Publish tested Python/framework/dependency versions. “Latest” and unsupported combinations are not implied guarantees.

## Release checklist

1. Freeze the release scope; triage all blocking defects and supported-claim failures.
2. Verify known broken/fixed scenarios, false-pass controls, privacy tests and compatibility.
3. Update changelog, roadmap status, migration notes, install docs and supported matrix.
4. Check licenses/notices, package metadata, authorship, included files and ignored sensitive artifacts.
5. Build clean artifacts and verify installation/quickstart from the actual wheel and source distribution.
6. Review the release diff and provenance; verify TestPyPI publishing and registry ownership.
7. Publish using the protected release path; attach checksums, SBOM, notes and provenance references.
8. Use immutable release assets/tags when enabled. Prepare draft release assets before publication; verify current host semantics.
9. Verify the public installation and advertised example from a clean environment.
10. Announce with supported scope and known limitations; monitor issues and record follow-up fixes.

Do not add badges before the workflows exist and pass. A plan file cannot serve as CI evidence.

## Rollback and incidents

Registry versions are not overwritten. For a defective release, assess whether to yank it, publish an advisory and release a new fixed version; document the last known good version and fixture migration limitations. Retain provenance and source history. An immutable release asset is not patched in place. Release-note corrections do not replace corrected code artifacts.

For compromised credentials/publisher: revoke access, disable the affected workflow, preserve logs, review artifact integrity, notify users through the advisory/release channel and rotate/re-establish publishing identity. Protect account recovery and require 2FA for registry/GitHub maintainers as available.

Local users can pin a previous supported package version and retain the original case files. Explicit schema migrations write new artifacts; never destructively rewrite all existing tests during an update. An optional feature can be disabled without breaking key-free regression execution.

## Observability and budgets

Structured local records cover import failure categories, execution completeness, rule outcomes, reduction attempts, elapsed time and artifact identity. They do not transmit telemetry. Aggregate local summaries are user-controlled and redacted. Keep model-token/spend reporting distinct from historical estimates and mocked usage.

CI has explicit job budgets, concurrency cancellation and bounded artifact retention. Review costs monthly during active work. Live-model jobs later use a separate dedicated credential/project with caps, no untrusted PR execution and explicit run authorization. Hosting and support service-level objectives belong to the commercial design, not volunteer OSS promises.

Sources: [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/), [PyPI attestations](https://docs.pypi.org/attestations/), [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use), [immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases), [PEP 440](https://peps.python.org/pep-0440/).
