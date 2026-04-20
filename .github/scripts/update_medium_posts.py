"""
Fetches latest Medium posts for santi020k and updates the README
with a visual card grid (image + title + date + excerpt).
"""

import re
import html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

FEED_URL = "https://medium.com/feed/@santi020k"
MAX_POSTS = 6  # 2 rows × 3 columns
COLS = 3

NAMESPACES = {
    "media": "http://search.yahoo.com/mrss/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


def fetch_feed(url: str) -> ET.Element:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return ET.fromstring(resp.read())


def get_image(item: ET.Element) -> str | None:
    # 1. media:content
    media = item.find("media:content", NAMESPACES)
    if media is not None and media.get("url"):
        return media.get("url")

    # 2. First <img src="..."> inside content:encoded
    node = item.find("content:encoded", NAMESPACES)
    if node is not None and node.text:
        m = re.search(r'src="(https://[^"]+)"', node.text)
        if m:
            return m.group(1)

    # 3. Fallback: description
    node = item.find("description")
    if node is not None and node.text:
        m = re.search(r'src="(https://[^"]+)"', node.text)
        if m:
            return m.group(1)

    return None


def get_excerpt(item: ET.Element, max_chars: int = 110) -> str:
    for node in [item.find("content:encoded", NAMESPACES), item.find("description")]:
        if node is not None and node.text:
            text = re.sub(r"<[^>]+>", "", node.text)
            text = html.unescape(text).strip()
            text = re.sub(r"\s+", " ", text)
            if len(text) > max_chars:
                text = text[:max_chars].rsplit(" ", 1)[0] + "…"
            return text
    return ""


def parse_date(raw: str) -> str:
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%b %d, %Y")
        except ValueError:
            continue
    return raw.strip()


def build_card(post: dict) -> str:
    img_tag = (
        f'<img src="{post["image"]}" width="270" alt="" /><br />'
        if post["image"]
        else ""
    )
    return (
        f'<td align="center" width="33%" valign="top">\n'
        f'  <a href="{post["url"]}">\n'
        f"    {img_tag}\n"
        f'    <strong>{html.escape(post["title"])}</strong>\n'
        f"  </a>\n"
        f'  <br /><sub>📅 {post["date"]}</sub>\n'
        f'  <br /><sub>{html.escape(post["excerpt"])}</sub>\n'
        f"</td>"
    )


def build_table(posts: list[dict]) -> str:
    rows = []
    for i in range(0, len(posts), COLS):
        chunk = posts[i : i + COLS]
        cells = "\n".join(build_card(p) for p in chunk)
        rows.append(f"<tr>\n{cells}\n</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def main():
    root = fetch_feed(FEED_URL)
    channel = root.find("channel")
    items = channel.findall("item")[:MAX_POSTS]

    posts = []
    for item in items:
        title = (item.findtext("title") or "").strip()
        url = (item.findtext("link") or "").strip()
        pub_date = parse_date(item.findtext("pubDate") or "")
        image = get_image(item)
        excerpt = get_excerpt(item)
        posts.append(
            {"title": title, "url": url, "date": pub_date, "image": image, "excerpt": excerpt}
        )

    table = build_table(posts)
    block = f"<!-- BLOG-POST-LIST:START -->\n{table}\n<!-- BLOG-POST-LIST:END -->"

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!-- BLOG-POST-LIST:START -->.*?<!-- BLOG-POST-LIST:END -->"
    new_content = re.sub(pattern, block, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ README updated with {len(posts)} posts")


if __name__ == "__main__":
    main()
