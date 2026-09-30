# Changelog

## 1.1.0 — 2026-09-30

- Added branded Website, Résumé, LinkedIn, Email, and availability badges.
- Centered the profile introduction and added a concise, responsive current-focus summary.
- Added a compact technology badge set that follows the existing violet visual language.
- Made the contribution snake visible by default while preserving the static reduced-motion alternative.

### Publication and recovery

Merging `release/v1.1.0` into `main` publishes the refreshed profile and triggers
the profile checks and Medium refresh. The contribution snake continues to use
the most recent images on the `output` branch. There is no package artifact, data
migration, or application deployment for this release.

Rollback is a reviewed revert of the merged release commit. External badge,
statistics, streak, and snake providers can be unavailable independently of the
repository and should be verified again after publication.

## 1.0.0 — 2026-09-30

First curated profile release, prepared on `release/v1.0.0`.

- Reorganized the profile around engineering leadership, developer tools, products,
  writing, and community work, with links to public evidence.
- Added light and dark violet headers and layouts that fit narrow screens.
- Restored GitHub statistics, language distribution, and contribution streak cards
  with theme-aware styling and disabled entrance animations.
- Restored the contribution snake as an optional expandable visual, with a static
  alternative for reduced motion and weekly generation.
- Replaced the Medium image grid with a compact, validated reading list.
- Added regression checks, maintenance instructions, and profile-settings suggestions.

### Publication and recovery

Merging the profile refresh from `release/v1.0.0` into `main` publishes the README
on GitHub and triggers the profile checks, Medium refresh, and contribution-snake
generation. Run the profile checks and the independent review required by the
global instructions before pushing the release branch. After merging, verify the
live profile and the first snake-generation workflow. This is a profile-content
release; there is no separately distributed application or package artifact.

There is no application runtime, package version, or data migration. If the
profile refresh needs to be rolled back, revert its merged change through the
normal reviewed workflow. The prior README and workflows remain in Git history;
the snake publisher preserves the history of the `output` branch. External cards
may be unavailable independently of a repository rollback.
