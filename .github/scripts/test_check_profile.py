"""Behavioral selection, history fallback and required-gate coverage."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_profile import ROOT, SUITES, compare, select


class SelectionTests(unittest.TestCase):
    def test_proven_scopes(self) -> None:
        self.assertEqual(select(["README.md"]), ("test_profile",))
        self.assertEqual(select(["assets/profile-dark.svg"]), ("test_profile",))
        self.assertEqual(select(["docs/profile-maintenance.md"]), ())
        self.assertEqual(select([".github/scripts/update_medium_posts.py"]), SUITES)
        self.assertEqual(select(["unknown.txt"]), SUITES)
        self.assertEqual(select(["README.md"], deleted=True), SUITES)

    def test_missing_history_and_renamed_deleted_sources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args: str) -> str:
                return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.PIPE).strip()
            git("init", "-q")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.test")
            (root / "README.md").write_text("Initial")
            git("add", ".")
            git("commit", "-qm", "initial")
            base = git("rev-parse", "HEAD")
            (root / "README.md").write_text("Changed")
            git("commit", "-qam", "change")
            self.assertEqual(compare(root, base), ("test_profile",))
            self.assertEqual(compare(root, "missing-ref"), SUITES)
            base = git("rev-parse", "HEAD")
            git("mv", "README.md", "renamed.md")
            git("commit", "-qam", "rename")
            self.assertEqual(compare(root, base), SUITES)

    def test_required_gate_rejects_unsuccessful_jobs(self) -> None:
        workflow = (ROOT / ".github/workflows/profile-check.yml").read_text()
        gate = workflow.split("      - name: Require both checks\n", 1)[1].split("        run: |\n", 1)[1]
        for result in ("failure", "cancelled", "skipped", ""):
            completed = subprocess.run(["bash", "-c", gate], env={"CHECKS": "success", "IMPACT": result}, capture_output=True)
            self.assertNotEqual(completed.returncode, 0, result)
        completed = subprocess.run(["bash", "-c", gate], env={"CHECKS": "success", "IMPACT": "success"}, capture_output=True)
        self.assertEqual(completed.returncode, 0)


if __name__ == "__main__":
    unittest.main()
