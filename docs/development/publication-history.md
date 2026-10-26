# Initial publication history preparation

26 October 2026. The owner approved preserving private development history and preparing a
clean initial publication snapshot. No GitHub repository, remote, push, visibility change,
release or package publication is authorized or performed by this step.

## Source and preservation

The source is private development revision `28ea014f6894844d0f3517a1c924f5f0d60a2342`:
144 tracked regular files, with no copied `.git` directory, environment, provider key, raw
trace, generated export, local report or dependency environment. The original repository
and its 18 commits remain intact. A separate private `git bundle --all` was created and
verified, preserving its branch refs and reachable history. Recovery files stay outside
this publication repository and are not included in its archives.

Application source, tests, examples, schemas, dependency locks, license texts and existing
attributions are byte-identical to the source snapshot. The only publication-preparation
changes are this record, the release-facts file, the GitHub runbook, the plan checklist and
the changelog. A private per-file hash comparison records that exact delta.

Earlier commit IDs in development verification records refer to retained private history.
They are dated engineering evidence, not links to commits in the new public Git graph.
This new initial snapshot does not claim new authorship or fabricate historical DCO sign-offs.
Owner source-rights/provenance review remains pending in the publication gate.

## Technical privacy checks

The publication repository is initialized independently, with one parentless `main` commit
and GitHub `noreply` author/committer attribution. It has no other branches, tags, remotes,
replacement refs, alternate/shared object store or unreachable development commit objects.
Original development commit IDs must not resolve as commit objects in this repository.

Checks cover tracked file contents, paths, the commit message/metadata and all Git objects.
Private owner addresses and the existing provider key are compared only in memory; their
values are never printed or recorded in reports. Token/private-key patterns are also checked.
The only permitted token-pattern matches are the two known synthetic privacy-test canaries,
which remain necessary test evidence. Environment, key, raw-trace, cache and recovery files
are excluded. The wheel/source archives are checked separately after building.

The exact new commit, tree and file/object counts, candidate artifact hashes, source-delta
manifest and backup integrity evidence are recorded in ignored local audit output. No private
recovery archive or original address is committed. Pattern checks are not a guarantee against
every possible secret; inspect newly added files and refs before every push.

## Verification and next approval

The new checkout uses its own environment and verifies that imports resolve to its source,
then runs the local test/quality/docs/package checks. The existing dated compatibility matrix
is retained; this copy step does not invent fresh hosted/platform results. The original demo
workspace and UI session are not migrated or modified.

Technical history privacy is separate from legal provenance and host readiness. Reporting
verification, actual GitHub CI/security settings, initial provenance review and final owner
acceptance remain pending. Future GitHub creation and the exact ref to push require a new
explicit owner-approved step. Never push the original private repository or recovery refs.
