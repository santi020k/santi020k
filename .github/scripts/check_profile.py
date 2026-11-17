"""Run only proven independent profile checks; uncertain input runs every suite."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SUITES = ("test_profile", "test_update_medium_posts")


def select(paths: list[str], deleted: bool = False) -> tuple[str, ...]:
    if deleted:
        return SUITES
    selected: set[str] = set()
    for path in paths:
        if path == "README.md" or path.startswith("assets/"):
            selected.add("test_profile")
        elif path in (".github/scripts/update_medium_posts.py", ".github/scripts/test_update_medium_posts.py"):
            selected.update(SUITES)
        elif path == ".github/scripts/test_profile.py":
            selected.add("test_profile")
        elif path.startswith("docs/") or path == "CHANGELOG.md":
            continue
        else:
            return SUITES
    return tuple(suite for suite in SUITES if suite in selected)


def compare(root: Path, base: str) -> tuple[str, ...]:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    try:
        ancestor = subprocess.check_output(
            ["git", "merge-base", "--", base, "HEAD"], cwd=root, env=environment,
            text=True, stderr=subprocess.PIPE).strip()
        records = subprocess.check_output(
            ["git", "diff", "--no-renames", "--name-status", "-z", ancestor, "HEAD"],
            cwd=root, env=environment, stderr=subprocess.PIPE).decode().split("\0")
        pairs = list(zip(records[0::2], records[1::2]))
        return select([path for _, path in pairs], any(status.startswith("D") for status, _ in pairs))
    except (subprocess.CalledProcessError, UnicodeError):
        return SUITES


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base")
    args = parser.parse_args()
    suites = compare(ROOT, args.base) if args.base else SUITES
    # The selector itself is never omitted, even for documentation-only changes.
    subprocess.run([sys.executable, "-m", "unittest", "-v", "test_check_profile", *suites],
                   cwd=ROOT / ".github/scripts", check=True)
    print("Selected profile suites: " + (", ".join(suites) or "selector only"))


if __name__ == "__main__":
    main()
