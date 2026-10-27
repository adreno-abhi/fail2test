# Private GitHub creation and first-push plan (completed)

Prepared 26 October 2026; retained as the historical operation plan. The owner subsequently
approved it, private creation/push completed, and merged `main` passed hosted CI on
27 October 2026. See [current host state](SETUP.md) and
[hosted CI evidence](../../development/hosted-ci.md). The steps below are not a request
to recreate the existing repository. Public visibility and package publication remain separate.

## Exact operation

| Item | Proposed value |
|---|---|
| Target | `adreno-abhi/fail2test`, owned by the confirmed account |
| Visibility | **Private**, including after the push |
| Description | Turn agent failures into reviewed, portable regression tests. |
| Source | This standalone publication checkout rooted at `8ef502f`; never the original development repository |
| Remote | `https://github.com/adreno-abhi/fail2test.git` |
| Ref | Reviewed HEAD to `refs/heads/main` only |
| Initialization | Empty repo; no generated README, license, gitignore or template history |
| Excluded | Public visibility, tags/releases, PyPI, Pages, model calls, secrets, paid services and auto-merge |

Authenticated lookup returned 404 again. That is not a reservation or proof against an
inaccessible repository. Stop on collision; do not overwrite, adopt or force-push an
existing repository without a new instruction.

## Access and spending boundaries

The connector can inspect GitHub but exposes no repository-creation tool in this session;
`gh` is not installed. The fallback is GitHub's signed-in browser UI, not token extraction
or an unapproved CLI installation. Git Credential Manager Core is installed/configured;
that does not establish valid authentication or an account match. Use its normal browser
sign-in if needed. Never print stored credentials or embed a token in a URL, script or chat.

**Before pushing, inspect Actions/billing controls. If included quota and blocked paid
overages cannot be verified, disable Actions on this new repo before the push.** Run CI
only within verified included quota or later explicit spending approval. Do not change
account-wide billing, buy a plan or enable paid security products.

## Execution after approval

1. Verify the browser account is `adreno-abhi`, the account-provided noreply address,
   recovery/privacy settings, the target collision check and the exact clean local HEAD.
   Confirm provenance; rescan new commits for private addresses, credentials and artifacts.
2. Create the **empty private** target. Verify actual owner and visibility; stop on mismatch.
   Apply the spending/Actions condition above before uploading any workflow-triggering ref.
3. Verify the remote has no refs. Add `origin` with the exact destination above in this
   publication checkout only. Add no other remotes, registry credentials or model secrets.
4. Push exactly `git push --set-upstream origin HEAD:refs/heads/main`, without force,
   all-refs, mirror or tag options. Pause for normal account sign-in if necessary; stop
   if unexpected remote refs appear. Never push private development/recovery refs.
5. Independently verify remote `main` equals the reviewed SHA, default branch is `main`,
   visibility remains private and no other refs were uploaded. Check community rendering
   and maintainer access; activate CODEOWNERS only after write/admin access is verified.
6. If quota permits authorized CI, run it and inspect actual matrix/browser/package checks,
   then apply supported protections from [SETUP.md](SETUP.md). Otherwise leave CI disabled
   and explicitly pending. No hosted pass is inferred from local tests.
7. Record URL, pushed SHA, visibility, CI state and verified host settings. Missing gate
   facts remain false. A private source push is not a public release or a passing gate.

## Outcome and recovery

The target remains private until a separately approved visibility step. Private vulnerability
reporting is a public-repository feature and remains unverified here. No source upload
implies public visibility, a release, registry registration or package publication.

On partial failure, leave the repo private and report exact state. Do not delete the repo,
force-update history, choose another destination or repeatedly retry failed authentication.
Local source and the verified private recovery bundle remain available. Do not claim a
deletion could retract copies already downloaded after any unintended upload.
