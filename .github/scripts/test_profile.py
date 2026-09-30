"""Check that the checked-in profile is usable without remote image services."""

from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ProfileTests(unittest.TestCase):
    def test_local_images_exist_and_have_accessible_alternatives(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        images = re.findall(r'<img\b[^>]*>', readme)
        self.assertTrue(images)
        for tag in images:
            self.assertRegex(tag, r'alt="[^"]+"')
        for path in re.findall(r'(?:src|srcset)="(\./[^"]+)"', readme):
            self.assertTrue((ROOT / path).is_file(), path)

    def test_theme_assets_are_static_self_contained_svg(self) -> None:
        for path in sorted((ROOT / "assets").glob("profile-*.svg")):
            with self.subTest(path=path.name):
                root = ET.parse(path).getroot()
                namespace = "{http://www.w3.org/2000/svg}"
                self.assertEqual(root.tag, namespace + "svg")
                self.assertIsNotNone(root.find(namespace + "title"))
                for node in root.iter():
                    self.assertNotIn(node.tag, [namespace + "script", namespace + "foreignObject", namespace + "animate"])
                    for name, value in node.attrib.items():
                        self.assertFalse(name.lower().startswith("on"))
                        if name.endswith("href"):
                            self.assertTrue(value.startswith("#"))

    def test_navigation_targets_exist(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        headings = {title.lower().replace(" ", "-") for title in re.findall(r"^## (.+)$", readme, re.MULTILINE)}
        for anchor in re.findall(r"\]\(#([^)]+)\)", readme):
            self.assertIn(anchor, headings)


if __name__ == "__main__":
    unittest.main()
