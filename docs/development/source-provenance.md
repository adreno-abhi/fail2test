# Initial source provenance review

26 October 2026. Reviewed the publication repository rooted at `8ef502f`, based on the
private source snapshot in [publication-history.md](publication-history.md). This records
inspected materials and origins; it is not a guarantee of originality, legal clearance or
permission to upload source.

## Scope and evidence

The initial snapshot contains 145 tracked text files. It was exported without development
Git objects, local keys, raw customer traces or recovery artifacts. Per-file hashes verify
unchanged application code, tests, examples, schemas, lockfile and license texts. The five
initial differences were release-preparation documents. Later review documents and release
facts are ordinary new commits on this clean history, not imported development commits.

| Material | Recorded origin and review |
|---|---|
| Runtime, CLI, UI, adapters, scripts and tests | Developed in this owner-directed, AI-assisted project. Repository policies disclose AI assistance and human accountability. No additional copied-source attribution was identified in inspected code/comments; this does not establish universal originality. |
| Refund examples and fixtures | Project-maintained synthetic scenarios, not live payment/model evidence. Token-shaped privacy-test strings are explicit synthetic canaries. |
| LICENSE | Matches official Apache-2.0 text after whitespace normalization; metadata, NOTICE and README identify the same license and separate exceptions. |
| Code of conduct | Contributor Covenant 3.0 adaptation; CC BY-SA 4.0 attribution, upstream links and reporting/enforcement changes are explicit. |
| DCO | DCO 1.1 matches the official document after whitespace normalization. No retroactive or third-person sign-off was created. |
| Python dependencies | All 82 locked third-party packages have inventory evidence, including the platform-specific exception. Packages are installed separately, not vendored into this tree. |
| Browser assets | Authored HTML/CSS/JavaScript with system fonts. No tracked binaries, model weights, downloaded fonts/images or vendored frontend framework were found. |
| CI actions | External references pinned to reviewed upstream commits; source is not vendored. Metadata and local workflow syntax were checked. |
| Planning/research | Historical authored plans/templates and cited research, explicitly subordinate to current root policies. Included license copies retain their text. |

The review searched code, tests, examples, scripts and planning material for copied/adapted
source notices, copyright and license declarations, then inspected the results. It is not
an external similarity search. It cannot determine undisclosed employment/IP obligations.
License inventory evidence is separate from vulnerability testing and legal compatibility.

## Owner confirmation

**Confirmed by the owner on 26 October 2026:** “I have permission; no unlisted/private
material was added.” This answers the explicit question about publication under the stated
licenses and employer/client code, confidential data or unlisted third-party additions.
Together with the inspection above, this completes the initial provenance review recorded
in `initial_provenance_reviewed`. It is not an independent legal clearance, a DCO sign-off,
or approval to create a repository, upload code or make it public.

## Verification and remaining gates

Official license/DCO comparisons passed; hashes are in ignored audit output. Inventory
consistency covers 82 packages. The preceding clean-checkout step passed 192 tests at 88%
combined coverage. This review changes documents/release facts, not application behavior.
Recheck new commit metadata and archives before upload. Host checks, live reporting and
final publication acceptance remain pending. The [first-push plan](../release/github/FIRST_PUSH.md)
is a proposed operation, subject to explicit owner approval.

## Primary sources

- [Apache-2.0 text](https://www.apache.org/licenses/LICENSE-2.0.txt)
- [Developer Certificate of Origin 1.1](https://developercertificate.org/)
- [Contributor Covenant 3.0](https://www.contributor-covenant.org/version/3/0/)
- [Project third-party declarations](../../THIRD_PARTY_NOTICES.md)
- [Locked dependency inventory](../licensing/dependencies.json)
