# Profile maintenance

This repository is Santiago Molina’s GitHub profile. `README.md` is the public
landing page; keep maintenance details here so the profile stays easy to scan.
It is a Markdown repository with standard-library Python automation, not an app
or a published package. It has no package manager, install step, or production build.
The first profile refresh uses `release/v1.0.0`; its changes and publication
procedure are tracked in `CHANGELOG.md`.

## Content structure

1. Identity, positioning, and direct contact links.
2. Selected professional work, linked to public case studies.
3. Six featured developer tools, followed by a short wider-ecosystem paragraph.
4. Four personal products, linked to public product websites.
5. Working principles and a compact technology summary.
6. Three curated website articles and three automatically refreshed Medium posts.
7. Community contributions and a recorded talk.
8. GitHub activity cards, an optional contribution snake, and a clear invitation to collaborate.

Keep the profile useful to engineering teams, hiring managers, and collaborators.
Describe the problem and the contribution before listing technologies. Avoid
unverified traction, stale version numbers, and lengthy badge grids. Keep activity
widgets below the portfolio content so they support the work rather than dominate it.
Only advertise availability when Santiago confirms it is current.

## Files

- `README.md`: editable profile copy; only the `BLOG-POST-LIST` block is generated.
- `assets/profile-light.svg` and `assets/profile-dark.svg`: editable, self-contained
  vector headers. Their colors follow the public
  [Santi020k Theme tokens](https://github.com/santi020k/santi020k-theme/blob/main/packages/theme/tokens/tokens.json).
  Use the same composition in each theme. The image must scale with its intrinsic
  aspect ratio; do not add a fixed HTML height.
- `.github/scripts/update_medium_posts.py`: refreshes the latest three Medium posts.
- `.github/scripts/test_*.py`: offline profile and feed regression checks.
- `.github/workflows/profile-check.yml`: checks pull requests and changes to `main`.
- `.github/workflows/blog-post-workflow.yml`: daily Medium refresh at 08:00 UTC,
  with a manual trigger restricted to `main`.
- `.github/workflows/snake.yml`: weekly contribution animation refresh, with
  light/dark violet palettes and incremental commits to the existing `output` branch.
- `assets/contribution-paused.svg`: static alternative when reduced motion is requested.
- `.github/workflows/apply-topics.yml`: existing, separately invoked repository-topic
  administration. It is not needed to update the profile.
- `banner.png`, `banner.webp`, and `old-banners/`: retained historical artwork.

GitHub renders the page with its own styles. Use semantic Markdown, compact
lists, and simple tables. Lumen’s runtime components cannot run in a GitHub
README, so no frontend dependency is needed. The static header reuses Theme’s
palette without requiring a build or a remote image service. Activity widgets use
external providers, as described below.

## GitHub widgets

- Statistics and languages use the maintained
  [GitHub Stats Extended](https://github.com/stats-organization/github-stats-extended)
  service. The original [GitHub Readme Stats](https://github.com/anuraghazra/github-readme-stats)
  project now recommends this successor; its old endpoints returned HTTP 503
  during this iteration.
- Contributions and streaks use
  [GitHub Readme Streak Stats](https://github.com/DenverCoder1/github-readme-streak-stats).
- Both providers have separate light/dark palettes; entrance animations are
  disabled. Cards wrap naturally on narrow screens. No private token is sent to
  a widget service, and no self-hosted infrastructure is required.
- The [contribution snake](https://github.com/Platane/snk) is opt-in through a
  collapsed details element. Reduced-motion viewers receive a static alternative.
  Its GitHub Actions job generates new images weekly and when its workflow changes
  on `main`. Generation must succeed before publication; `keep_history: true`
  preserves existing output history. It runs independently of the Medium refresh.
- The old activity-graph endpoint returned HTTP 402, so it is not embedded.

These cards are cached, provider-calculated snapshots. Language totals describe
public repository code, not skill level; counts across providers need not agree.
Check the SVG's displayed content, not only HTTP status, before declaring a widget
healthy. Keep ordinary links to GitHub usable when providers are down.

The snake references the last published `output` images. Changes to its palette
appear after a successful authorized workflow run on `main`; a local preview
does not demonstrate that publication.

The restored actions are pinned to verified stable releases: snk 3.5.0 and
ghaction-github-pages 5.0.0. The publisher uses Node 24 and requires an Actions
runner at least 2.327.1; GitHub-hosted `ubuntu-latest` is the intended environment.

## Source review

Reviewed on September 30, 2026 (UTC). Local project READMEs were cross-checked
against public GitHub repository visibility and public product pages. Public
copy should always have a public source; private repository contents are not
permission to disclose unreleased projects, client internals, or family information.

| Profile content | Public source |
| --- | --- |
| Name, positioning, career since 2014, contact | [Website](https://santi020k.com/), [résumé](https://santi020k.com/resume/), [GitHub](https://github.com/santi020k) |
| Leadership and professional work | [Void](https://santi020k.com/portfolio/void/), [X Games](https://santi020k.com/portfolio/xgames/), [Smith Commerce](https://santi020k.com/portfolio/smith-commerce/), [Optic Power](https://santi020k.com/portfolio/optic-power/) |
| Maintained tools and the relationships between them | [Public repositories](https://github.com/santi020k?tab=repositories), [developer-tool ecosystem article](https://santi020k.com/blog/building-santi020k-developer-tool-ecosystem/) |
| Product scope | [PostLens](https://postlens.santi020k.com/), [Between Contractions](https://between.santi020k.com/), [RoadScore](https://roadscore.santi020k.com/), [Coolstead](https://coolstead.santi020k.com/) |
| Writing | [Website articles](https://santi020k.com/blog/), [Medium RSS](https://medium.com/feed/@santi020k) |
| Community and talks | [ReactJS Colombia](https://santi020k.com/portfolio/react-js-colombia/), [speaking archive](https://santi020k.com/speaking/) |
| Professional-network link | [LinkedIn](https://linkedin.com/in/santi020k) |

LinkedIn returned a browser challenge during direct verification; its indexed
public result was available, but a current authenticated profile was not reviewed.
Medium’s article pages blocked direct automated requests; the author feed returned
its latest published titles, dates, and links successfully. Do not confuse a 200
response containing a browser challenge with verified profile content.

Keep source-available licensing distinct from open source: Observatory is described
as source-available. Auth has its own integration and maturity constraints; avoid
claiming universal or production-ready authentication. Private-source products
link to their public websites, not inaccessible source repositories. Store approval,
launch status, and version claims require a fresh public check before adding them.

## Update and verify

Use Python 3.10 or newer; GitHub Actions uses Python 3.12. No Python dependencies
are required.

```sh
python3 -m unittest discover -s .github/scripts -p 'test_*.py' -v
python3 .github/scripts/update_medium_posts.py
python3 -m compileall -q .github/scripts
git diff --check
```

When workflows change, also run `actionlint` if available. Run the refresh twice
and confirm the second run produces no further change. The updater sorts by
publication time, excludes future/invalid items, removes tracking parameters,
deduplicates URLs, escapes output, and preserves the README when fetching or
validation fails. The only accepted article hosts are Medium and Towards Dev;
verify and add a host if a new publication is used. An atomic replacement protects
the existing file if writing fails.

Render the Markdown through GitHub’s Markdown API or GitHub’s preview. Check light
and dark themes at desktop and narrow mobile widths. Check image loading, banner
proportions, section links, text wrapping, table overflow, and keyboard focus.
Also verify all widget images load, inspect their visible values for provider-error
cards, expand the snake, and check its reduced-motion alternative.
Before/after captures should use the same viewport, theme, and rendering surface.
Local previews approximate GitHub’s surrounding layout; the final live profile must
be checked after an authorized push and merge. Keep screenshots out of Git.

Quality was evaluated for this repository; its current automatic detection finds
no applicable analyzers here. The standard-library test command is the completion
gate. Astro Doctor, ESLint, OG generation, Auth, and a JavaScript package manager
would add no useful capability to this static profile and are not dependencies.

## Suggested GitHub setup

These are recommendations for an authorized profile-settings update, not changes
made by this repository.

**Bio draft**

> Engineering leader & full-stack architect. Building developer tools and native products. ReactJS Colombia co-organizer. Medellín · Remote worldwide.

**Six recommended pins, in order**

1. `lumen`: design systems and accessible UI.
2. `astro-doctor`: framework tooling and diagnostics.
3. `quality`: systems tooling across languages.
4. `eslint-config-basic`: maintainable JavaScript and TypeScript standards.
5. `dep-beacon`: editor integrations and dependency intelligence.
6. `santi020k-theme`: a cohesive, cross-tool visual identity.

**LinkedIn headline draft**

> Engineering Leader & Full-Stack Architect | Developer Experience, Design Systems & Native Products | ReactJS Colombia

**Suggested LinkedIn Featured links**

- [Professional work](https://santi020k.com/work/).
- [Developer-tool ecosystem article](https://santi020k.com/blog/building-santi020k-developer-tool-ecosystem/).
- [Lumen UI](https://lumen.santi020k.com/).
- [Speaking and community](https://santi020k.com/speaking/).

Do not automatically alter GitHub pins, bio, LinkedIn, repository topics, or
website content. Keep iteration commits on the active release branch. Publishing the README
requires an authorized push and merge through the repository’s normal GitHub
workflow. Creating a release branch alone does not publish a profile, tag, or release.
