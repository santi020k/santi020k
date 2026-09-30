# Changelog

## 1.0.0 — Unreleased

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

This release is being iterated locally. No profile publication, tag, or GitHub
Release has been created. Before an authorized push or PR into `main`, run the
profile checks and the independent review required by the global instructions.
After merging, verify the live profile and the first snake-generation workflow.

There is no application runtime, package version, or data migration. If the
profile refresh needs to be rolled back, revert its merged change through the
normal reviewed workflow. The prior README and workflows remain in Git history;
the snake publisher preserves the history of the `output` branch. External cards
may be unavailable independently of a repository rollback.
