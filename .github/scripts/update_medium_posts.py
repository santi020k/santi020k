"""Refresh the compact Medium reading list without changing the curated profile."""

from __future__ import annotations

import html
import sys
import tempfile
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

FEED_URL = "https://medium.com/feed/@santi020k"
MAX_POSTS = 3
MAX_FEED_BYTES = 2_000_000
START_MARKER = "<!-- BLOG-POST-LIST:START -->"
END_MARKER = "<!-- BLOG-POST-LIST:END -->"
README_PATH = Path(__file__).resolve().parents[2] / "README.md"
POST_HOSTS = {"medium.com", "www.medium.com", "towardsdev.com", "www.towardsdev.com"}


@dataclass(frozen=True)
class Post:
    title: str
    url: str
    published: datetime


def fetch_feed(url: str) -> ET.Element:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        content = response.read(MAX_FEED_BYTES + 1)
    if len(content) > MAX_FEED_BYTES:
        raise ValueError("Feed exceeds the size limit")
    return ET.fromstring(content)


def clean_url(raw: str) -> str:
    """Allow known publication hosts and remove RSS attribution parameters."""
    try:
        url = urlsplit(raw.strip())
        if (
            url.scheme != "https"
            or url.hostname not in POST_HOSTS
            or url.username is not None
            or url.password is not None
            or url.port not in (None, 443)
            or not url.path.strip("/")
        ):
            return ""
    except ValueError:
        return ""
    return urlunsplit(("https", url.hostname, url.path, "", ""))


def parse_posts(root: ET.Element, now: datetime | None = None) -> list[Post]:
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Expected an RSS channel")
    current_time = now if now is not None else datetime.now(timezone.utc)
    posts: list[Post] = []
    for item in channel.findall("item"):
        title = " ".join((item.findtext("title") or "").split())
        url = clean_url(item.findtext("link") or "")
        try:
            published = parsedate_to_datetime(item.findtext("pubDate") or "")
        except (TypeError, ValueError, OverflowError):
            continue
        if not title or not url or published.tzinfo is None or published > current_time:
            continue
        posts.append(Post(title, url, published))

    unique: dict[str, Post] = {}
    for post in sorted(posts, key=lambda post: post.published, reverse=True):
        unique.setdefault(post.url, post)
    result = list(unique.values())[:MAX_POSTS]
    if not result:
        raise ValueError("Feed has no valid published posts; keeping the existing list")
    return result


def build_list(posts: list[Post]) -> str:
    items = []
    for post in posts:
        date = post.published.astimezone(timezone.utc).strftime("%b %d, %Y")
        items.append(
            f'  <li><a href="{html.escape(post.url, quote=True)}">'
            f"{html.escape(post.title)}</a> · {date}</li>"
        )
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


def replace_posts(content: str, posts: list[Post]) -> str:
    if content.count(START_MARKER) != 1 or content.count(END_MARKER) != 1:
        raise ValueError("README must contain exactly one pair of blog markers")
    start = content.index(START_MARKER) + len(START_MARKER)
    end = content.index(END_MARKER)
    if end < start:
        raise ValueError("Blog markers are in the wrong order")
    return content[:start] + "\n" + build_list(posts) + "\n" + content[end:]


def update_readme(path: Path, root: ET.Element) -> int:
    posts = parse_posts(root)
    content = path.read_text(encoding="utf-8")
    updated = replace_posts(content, posts)
    if updated != content:
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent, delete=False
            ) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(updated)
            temporary_path.chmod(path.stat().st_mode)
            temporary_path.replace(path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
    return len(posts)


def main() -> int:
    try:
        count = update_readme(README_PATH, fetch_feed(FEED_URL))
    except (OSError, urllib.error.URLError, ET.ParseError, ValueError) as error:
        print(f"Medium refresh failed ({type(error).__name__}); README unchanged.", file=sys.stderr)
        return 1
    print(f"README refreshed with {count} Medium posts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
