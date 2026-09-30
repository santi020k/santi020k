"""Behavioral checks for an automated edit to the public profile."""

from __future__ import annotations

import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import update_medium_posts as feed

NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)


def make_feed(items: list[tuple[str, str, str]]) -> ET.Element:
    root = ET.Element("rss")
    channel = ET.SubElement(root, "channel")
    for title, url, date in items:
        item = ET.SubElement(channel, "item")
        for name, value in (("title", title), ("link", url), ("pubDate", date)):
            ET.SubElement(item, name).text = value
    return root


def article(day: int, title: str = "A useful article") -> tuple[str, str, str]:
    return title, f"https://medium.com/@santi020k/post-{day}", f"Tue, {day:02} Sep 2026 10:00:00 GMT"


class FeedTests(unittest.TestCase):
    def test_sorts_limits_and_deduplicates_tracking_variants(self) -> None:
        title, url, date = article(5)
        root = make_feed([article(1), article(4), article(2), (title, url + "?source=rss", date), article(5)])
        posts = feed.parse_posts(root, NOW)
        self.assertEqual([post.url.rsplit("-", 1)[-1] for post in posts], ["5", "4", "2"])

    def test_accepts_medium_publications_and_removes_tracking(self) -> None:
        self.assertEqual(
            feed.clean_url("https://towardsdev.com/my-article?source=rss#section"),
            "https://towardsdev.com/my-article",
        )

    def test_rejects_unsafe_and_unrecognized_destinations(self) -> None:
        for url in (
            "javascript:alert(1)",
            "http://medium.com/post",
            "https://medium.com.evil.example/post",
            "https://evil.example/post",
            "https://user:password@medium.com/post",
            "https://medium.com:444/post",
            "https://medium.com:bad/post",
            "https://medium.com/",
            "https://[broken",
        ):
            with self.subTest(url=url):
                self.assertEqual(feed.clean_url(url), "")

    def test_skips_missing_fields_invalid_dates_and_future_posts(self) -> None:
        root = make_feed([
            ("", "https://medium.com/post", article(1)[2]),
            ("No link", "", article(1)[2]),
            ("No date", "https://medium.com/post", ""),
            ("Invalid date", "https://medium.com/post", "not a date"),
            ("No timezone", "https://medium.com/post", "Tue, 01 Sep 2026 10:00:00"),
            ("Future", "https://medium.com/future", "Wed, 01 Sep 2027 10:00:00 GMT"),
            article(1),
        ])
        self.assertEqual(len(feed.parse_posts(root, NOW)), 1)

    def test_missing_channel_and_empty_feed_fail_closed(self) -> None:
        for root in (ET.Element("html"), make_feed([])):
            with self.subTest(root=root.tag), self.assertRaises(ValueError):
                feed.parse_posts(root, NOW)

    def test_title_and_attributes_are_escaped(self) -> None:
        post = feed.Post('<img src=x onerror="alert(1)"> & news', 'https://medium.com/a"b', NOW)
        rendered = feed.build_list([post])
        self.assertNotIn("<img", rendered)
        self.assertIn("&lt;img", rendered)
        self.assertIn("&amp; news", rendered)
        self.assertIn('href="https://medium.com/a&quot;b"', rendered)

    def test_only_the_generated_section_changes(self) -> None:
        content = f"# My profile\n{feed.START_MARKER}\nOld posts\n{feed.END_MARKER}\nMy projects"
        posts = feed.parse_posts(make_feed([article(1)]), NOW)
        updated = feed.replace_posts(content, posts)
        self.assertTrue(updated.startswith(f"# My profile\n{feed.START_MARKER}\n"))
        self.assertTrue(updated.endswith(f"\n{feed.END_MARKER}\nMy projects"))
        self.assertNotIn("Old posts", updated)
        self.assertEqual(feed.replace_posts(updated, posts), updated)

    def test_invalid_markers_fail_without_replacing_content(self) -> None:
        for content in (
            "No markers",
            feed.START_MARKER,
            feed.END_MARKER + feed.START_MARKER,
            feed.START_MARKER * 2 + feed.END_MARKER,
            feed.START_MARKER + feed.END_MARKER * 2,
        ):
            with self.subTest(content=content), self.assertRaises(ValueError):
                feed.replace_posts(content, [])

    def test_invalid_feed_does_not_erase_existing_readme(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            original = f"Profile\n{feed.START_MARKER}\nSaved posts\n{feed.END_MARKER}"
            path.write_text(original, encoding="utf-8")
            with self.assertRaises(ValueError):
                feed.update_readme(path, make_feed([]))
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_successful_update_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(f"{feed.START_MARKER}\n{feed.END_MARKER}", encoding="utf-8")
            root = make_feed([article(1)])
            self.assertEqual(feed.update_readme(path, root), 1)
            first = path.read_bytes()
            self.assertEqual(feed.update_readme(path, root), 1)
            self.assertEqual(path.read_bytes(), first)

    def test_network_failure_returns_failure_without_attempting_a_write(self) -> None:
        with (
            patch.object(feed, "fetch_feed", side_effect=TimeoutError),
            patch.object(feed, "update_readme") as update,
            patch("sys.stderr"),
        ):
            self.assertEqual(feed.main(), 1)
            update.assert_not_called()

    def test_filesystem_failure_preserves_original_and_cleans_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            original = f"{feed.START_MARKER}\nSaved posts\n{feed.END_MARKER}"
            path.write_text(original, encoding="utf-8")
            with patch.object(Path, "replace", side_effect=OSError), self.assertRaises(OSError):
                feed.update_readme(path, make_feed([article(1)]))
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_oversized_feed_is_rejected(self) -> None:
        with patch.object(feed.urllib.request, "urlopen") as request:
            request.return_value.__enter__.return_value.read.return_value = b"x" * (feed.MAX_FEED_BYTES + 1)
            with self.assertRaisesRegex(ValueError, "size limit"):
                feed.fetch_feed(feed.FEED_URL)


if __name__ == "__main__":
    unittest.main()
