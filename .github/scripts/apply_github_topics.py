"""
Apply GitHub repository topics via the REST API (requires a token with repo scope).

Usage:
  GITHUB_TOKEN=ghp_... python .github/scripts/apply_github_topics.py

Uses GITHUB_TOKEN or GH_TOKEN from the environment. If unset, prints a message and exits 0.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

OWNER = "santi020k"

# Curated topics for discoverability (GitHub: lowercase, hyphenated, <=20 topics each).
REPO_TOPICS: dict[str, list[str]] = {
    "next-meetup": ["nextjs", "react", "meetup", "legacy", "javascript"],
    "eslint-config-basic": [
        "eslint",
        "typescript",
        "javascript",
        "react",
        "nextjs",
        "astro",
        "developer-experience",
        "flat-config",
        "lint",
    ],
    "eslint-config-santi020k": [
        "eslint",
        "typescript",
        "javascript",
        "react",
        "legacy",
    ],
    "file-manager": ["nextjs", "typescript", "tailwindcss", "vercel", "cloud-storage", "file-picker"],
    "interviews": ["vue", "vite", "react", "technical-interviews", "meetup", "slides"],
    "void": ["typescript", "nextjs", "nx", "monorepo", "microfrontend"],
    "medium-posts": ["nextjs", "typescript", "blog", "examples", "medium"],
}


def put_topics(repo: str, names: list[str], token: str) -> None:
    url = f"https://api.github.com/repos/{OWNER}/{repo}/topics"
    body = json.dumps({"names": names}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="PUT",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()
    print(f"OK {repo} -> {', '.join(names)}")


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("No GITHUB_TOKEN or GH_TOKEN set; skipping topic updates.")
        print("Create a fine-grained PAT with Contents read/write on these repos, or classic PAT with repo scope.")
        return
    for repo, topics in REPO_TOPICS.items():
        try:
            put_topics(repo, topics, token)
        except urllib.error.HTTPError as e:
            print(f"ERR {repo}: HTTP {e.code} {e.reason} — {e.read().decode(errors='replace')[:200]}")


if __name__ == "__main__":
    main()
