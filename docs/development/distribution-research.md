# Distribution research for Fail2Test v0.1.0

Checked 2 November 2026 against the primary sources linked below. This is preparation,
not permission to post, create accounts, contact maintainers or submit listing PRs.
Some retrieved pages are cached; recheck the actual venue's rules before a submission.

## Recommendation

Build distribution around a precise developer problem: a Python/LangGraph agent executed
the same tool action twice, and a reviewed regression now catches that bug in current code.
Use project-owned GitHub assets and a useful tutorial as the durable destination. Seek
relevant users in communities that explicitly permit showcasing; broaden only after a few
external integrations produce evidence and stories. This is a fit judgment, not measured
conversion evidence. Personal LinkedIn posting is unnecessary; human maintainer presence,
honest affiliation and responses to technical questions remain necessary.

There is no reliable way to guarantee views, GitHub Trending or virality. A new release alone
does not establish distribution. Do not buy stars, organize votes, use sockpuppets or let
generated comments impersonate users. A channel that forbids promotional/generated text
does not become suitable because the project is open source.

## Prioritized routes

### 1. GitHub project presence — do first

GitHub topics help developers find relevant repositories and related projects. Add a small,
accurate set such as `python`, `pytest`, `regression-testing`, `langgraph`, `ai-agents` and
`developer-tools`, rather than unrelated trending labels. GitHub supports up to 20 topics.
This improves classification, not a guaranteed rank or traffic result.
[GitHub topic documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics).

Put a short demonstration and the exact key-free try path near the README's top. A custom
social preview can replace the default owner-avatar card: GitHub recommends 1280×640 for
best display and requires an image under 1 MB. This is a project-brand asset; a personal
profile post is not required. Upload is a separate external action.
[GitHub social-preview documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview).

The principal conversion ask should be to reproduce the example and then integrate one
actual failure, with a safe way to report friction. Stars are optional attention signals.
Neither clone counts nor stars prove the generated test is used in a real application.

### 2. LangChain Community Slack — strong fit, conditional submission

The official LangChain community page describes Slack as a place to connect with developers
and learn about their projects. The forum's own guidelines direct showcases and broader
conversation to that Slack community. This supports Slack as a candidate route for the
native LangGraph example; it does not establish a specific channel name or permission to
advertise anywhere in the workspace. Join/read its current channel rules first, then use
only the permitted showcase channel and disclose maintainership. Workspace membership and
moderation requirements were not inspected behind sign-in.
[Official community page](https://www.langchain.com/community),
[forum guidelines](https://forum.langchain.com/guidelines).

**Do not launch in the LangChain Forum.** Its guidelines prohibit promotional content or
solicitation and disallow external-link answers except LangChain documentation. Do not
disguise a product link as a support answer. Genuine technical participation must obey those
restrictions. This is a concrete reason to separate Slack discovery from the help forum.
[Forum rules](https://forum.langchain.com/guidelines).

### 3. Show HN — useful runnable-project channel, human-authored only

Show HN is for substantive things people can try, including software run on their own
computers. Its guidance favors easy access without signups and expects the maker to explain
the work and be available for discussion. A README/demo with a runnable key-free example is
therefore a better submission destination than a signup page or promotional blog article.
Minor version announcements are generally not a fresh Show HN; ask-for-upvotes campaigns
are prohibited. Eligibility does not promise front-page placement.
[Show HN rules](https://news.ycombinator.com/showhn.html).

HN's current general guidelines prohibit generated text in posts, generated or AI-edited
comments, and automated posting. They also discourage using HN primarily for promotion,
requesting votes/comments and deleting/reposting. **Do not paste an AI-written launch draft
or AI-edited owner text into HN.** A factual checklist can help the owner understand what to
cover, but the owner needs to compose the submission and replies themselves, without AI
writing/editing. Project code being AI-assisted is a separate matter from posting generated
text; do not conceal the project's actual provenance when asked.
[HN guidelines](https://news.ycombinator.com/newsguidelines.html).

### 4. Project-branded technical articles; DEV has important restrictions

DEV supports free organization accounts for open source projects, with an organization
landing page, branding and analytics. A member DEV account is required before creating an
organization, so this is project branding rather than an anonymous publishing mechanism.
No organization was created in this research.
[DEV organization help](https://dev.to/help/organizations),
[creation procedure](https://dev.to/help/organizations/creating-and-managing-organizations).

An AI-drafted promotional tutorial is **not DEV-ready**: DEV's AI guidelines require
disclosure and accuracy checking, but also say AI-assisted/generated articles should not
promote a business, program or course, including the author's own, or principally build
brand/social presence. AI-generated comments are prohibited apart from specified assistive
exceptions. Merely adding an AI disclosure does not remove the promotion restriction.
Prefer publishing the prepared project tutorial on the project's own docs/blog. For DEV,
use a genuinely human-authored educational article or obtain editorial clarification for
the proposed format; do not assume an OSS project is exempt.
[DEV AI guidelines](https://dev.to/guidelines-for-ai-assisted-articles-on-dev),
[DEV code of conduct](https://dev.to/code-of-conduct).

### 5. Curated ecosystem lists — defer until there is evidence of use

`kyrolabs/awesome-langchain` is topically relevant and its README welcomes contributions,
but the authoritative contribution policy is more restrictive: projects should be maintained,
high quality, provide clear added value and demonstrate traction. It explicitly excludes
brand-new repositories without demonstrated traction. It requests a PR rather than an issue,
with the item at the bottom of its appropriate list, and says unsuitable PRs may be closed
automatically. Thus a day-one submission is a poor bet. First gather genuine external use
and maintainer history; afterward propose a concise entry backed by the integration example.
No acceptance, review time or newsletter placement is promised.
[Repository](https://github.com/kyrolabs/awesome-langchain),
[actual contribution rules](https://github.com/kyrolabs/awesome-langchain/blob/main/contributing.md).

Do not submit the individual product to the root `sindresorhus/awesome` index as if it were
an awesome list. Its contribution guide distinguishes adding lists from contributing items
to a topic list. The receiving topic list's own policy determines suitability.
[Awesome contribution guide](https://github.com/sindresorhus/awesome/blob/main/contributing.md).

## Reddit: restrictive, lower-priority routes

The ordinary rules pages rendered incomplete shells, but the official JSON endpoints were
readable. `r/LangChain` has an explicit no-solicitation/self-promotion rule; it permits sharing
projects/learnings about LangChain products but excludes vendor/recruiter/competitor lead
generation. Because our contemplated action is a launch promotion, do not treat that broad
project language as permission. Seek moderator clarification only in a separately authorized
step if this becomes important; do not promote there by default.
[Official r/LangChain rules](https://www.reddit.com/r/LangChain/about/rules.json).

`r/LocalLLaMA` requires relevant LLM content, limits self-promotion to roughly 10% of activity,
requires affiliation disclosure, prohibits bots posing as humans, and rejects completely or
primarily LLM-generated copy/code. The narrow disclosed translation/refinement exception is
for non-native/non-English speakers. It is a weaker initial audience fit for a fixture-testing
tool than LangGraph builders, and a new project account cannot assume permission to launch
there. Do not supply a ready-to-paste AI draft or make manufactured participation to satisfy a
ratio. This is a conditional future channel, not a day-one promise.
[Official r/LocalLLaMA rules](https://www.reddit.com/r/LocalLLaMA/about/rules.json).

## Measurement without personal social posting or hidden telemetry

GitHub's repository traffic view is available on public Free-plan repositories to users with
push access. It includes full clones (not fetches), recent visitors, referring sites and popular
content over a 14-day window. Traffic data uses UTC, with visitors/clones updated hourly and
referrer/content data daily. Referrers exclude search engines and GitHub itself. Save a dated
weekly snapshot; do not expect a complete source-attribution funnel or historical reporting
from a single later visit.
[GitHub traffic documentation](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-traffic-to-a-repository).

Use aggregate attention data alongside voluntary, concrete adoption evidence: useful external
issues, reproducible installation friction, a regression integrated into an external application,
repeat use confirmed by that developer, and independent contributions. Our own CI/demo clones,
bots, reinstallations and curiosity downloads can inflate acquisition counts. Do not infer a
number of active users or conversion rate from clones alone, and do not add telemetry merely
to make a dashboard look complete. Weekly small experiments can test messaging/channel fit;
their numerical goals must be labeled planning targets rather than forecasts.

## Practical sequence

1. Finish the real demonstration, exact-version quickstart, project preview and appropriate
   GitHub metadata. Keep scope/limitations prominent; choose one clear action for new visitors.
2. Publish one durable, reproducible technical walkthrough on a project-owned destination
   after approval, and invite voluntary integration feedback through the project's normal
   support route. No personal LinkedIn post is required.
3. Test one well-matched, permitted community route at a time. Slack showcase requires its
   actual workspace rules; Show HN requires the owner to write and participate personally.
4. Address onboarding defects promptly and publish useful examples of actual failures only
   with permission and safe synthetic reproductions. Revisit curated lists after external use.
5. Compare weekly traffic snapshots with independent integration evidence. More views with no
   successful integrations suggests an onboarding/fit issue, not a need for indiscriminate posting.

No outreach, posting, account creation, vote solicitation or listing PR occurred during this
research. These recommendations do not guarantee traction or endorse evading venue rules.
