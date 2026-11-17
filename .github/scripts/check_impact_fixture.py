"""Exercise the published Quality CLI against committed profile fixtures."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    binary = os.environ.get("QUALITY_BINARY", "quality")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        def git(*args: str) -> str:
            return subprocess.check_output(["git", *args], cwd=root, env=environment, text=True, stderr=subprocess.PIPE).strip()
        def selected(base: str) -> list[str]:
            plan = json.loads(subprocess.check_output(
                [binary, "impact", "plan", "--base", base, "--head", "HEAD", "--format", "json"],
                cwd=root, env=environment, text=True))
            return sorted(node["id"] for node in plan["selected"])
        git("init", "-q")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.test")
        shutil.copyfile(ROOT / "quality-impact.json", root / "quality-impact.json")
        git("add", ".")
        git("commit", "-qm", "policy")
        for path, expected in [
            ("README.md", ["profile", "selection"]),
            ("docs/note.md", ["selection"]),
            (".github/scripts/update_medium_posts.py", ["automation", "profile", "selection"]),
            ("unknown.txt", ["automation", "profile", "selection"]),
        ]:
            base = git("rev-parse", "HEAD")
            file = root / path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("fixture")
            git("add", ".")
            git("commit", "-qm", "fixture")
            if selected(base) != expected:
                raise AssertionError(path)
        if selected("missing-ref") != ["automation", "profile", "selection"]:
            raise AssertionError("Missing history must select all nodes")
        base = git("rev-parse", "HEAD")
        git("rm", ".github/scripts/update_medium_posts.py")
        git("commit", "-qm", "delete automation")
        if selected(base) != ["automation", "profile", "selection"]:
            raise AssertionError("Deleted automation must select all nodes")
    print("Quality profile policy fixtures passed")


if __name__ == "__main__":
    main()
