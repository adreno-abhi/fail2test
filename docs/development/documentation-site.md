# Public documentation deployment

The site is built from `docs/site` using the existing locked MkDocs dependencies and
published to `https://adreno-abhi.github.io/fail2test/`. No custom domain or paid service
is required. The source repository remains the place for issues, contributions and releases.
The website is static documentation; it does not execute user evidence or host the local UI.

## Deployment contract

`.github/workflows/pages.yml` waits for successful push CI on `main`, checks out that exact
commit and builds with `mkdocs build --strict`. Fork PRs and failing CI cannot trigger a
deployment through this route. A maintainer can also manually dispatch the workflow from
`main`; that is an explicit recovery action and should use an already verified commit.
Only the generated `site` folder is uploaded. Draft launch materials, source workspaces,
secrets and ignored analytics are not deployment inputs. The home page's demo image uses
a pinned public repository asset rather than duplicating binary media.

Actions are pinned to commit SHAs. Build permissions are read-only; only the deployment
job has `pages: write` and `id-token: write`, through the `github-pages` environment.
Repository Pages settings must use **GitHub Actions**, with the environment limited to
the protected `main` branch. Existing source branch protection is preserved.

## Verify and recover

Run `.venv/Scripts/mkdocs build --strict` locally on Windows, or `uv run mkdocs build --strict`.
Inspect the homepage and navigation at desktop and narrow widths; check the quickstart,
walkthrough, feedback, repository and release links. Confirm the hosted deployment succeeds
and loads at the `/fail2test/` project path, including its CSS and search files.

For a content mistake, submit a correcting PR and let successful main CI redeploy. For a
failed deployment, inspect the build/deploy job before retrying the same verified commit.
Do not disable branch protection or expose a local workspace to repair a docs deployment.
GitHub Pages is available for public repositories on GitHub Free; service availability and
editorial/newsletter placement are not guarantees.

Reference: [GitHub's custom Pages workflow guidance](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
