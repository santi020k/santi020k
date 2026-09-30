# Changelog

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
