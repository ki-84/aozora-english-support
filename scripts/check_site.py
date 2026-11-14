#!/usr/bin/env python3
"""Check the built Pages output, including paths under the repository base URL."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
CONFIG = json.loads((ROOT / "site.json").read_text())
BASE = CONFIG["base_url"].rstrip("/") + "/"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs, self.images, self.meta = set(), [], [], {}
        self.headings = 0
        self.lang = None
        self.canonical = None
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, "Duplicate ID: " + attrs["id"]
            self.ids.add(attrs["id"])
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "h1":
            self.headings += 1
        if tag == "meta" and "name" in attrs:
            self.meta[attrs["name"]] = attrs.get("content", "")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "img":
            assert "alt" in attrs, "Image needs alt text (empty for decorative images)"
            self.images.append(attrs["src"])
        for attr in ("href", "src"):
            if attr in attrs:
                self.refs.append(attrs[attr])
        if "aria-controls" in attrs:
            self.refs.extend("#" + value for value in attrs["aria-controls"].split())


def target(url):
    parsed = urlparse(url)
    base = urlparse(BASE)
    if parsed.netloc != base.netloc or not parsed.path.startswith(base.path):
        return None
    path = OUT / unquote(parsed.path[len(base.path):])
    if parsed.path.endswith("/"):
        path /= "index.html"
    return path, unquote(parsed.fragment)


def main():
    paths = sorted(OUT.rglob("*.html"))
    assert len(paths) == 5, "Expected four public pages and a 404 page"
    pages = {path: Page(path) for path in paths}
    checked = 0
    for path, page in pages.items():
        assert page.lang == "ja", path
        assert page.headings == 1, (path, "Expected one h1")
        assert page.meta.get("description"), path
        assert page.meta.get("viewport"), path
        assert page.canonical.startswith(BASE), path
        url = BASE + path.relative_to(OUT).as_posix().removesuffix("index.html")
        for ref in page.refs:
            parsed = urlparse(ref)
            assert parsed.scheme not in {"http", "mailto", "javascript"}, (path, ref)
            resolved = target(urljoin(url, ref))
            if resolved:
                dest, fragment = resolved
                assert dest.is_file(), (path, "Missing file", ref)
                if fragment:
                    assert dest in pages and fragment in pages[dest].ids, (path, "Missing fragment", ref)
            checked += 1
    home = (OUT / "index.html").read_text()
    books = json.loads((ROOT / "src/books.json").read_text())
    assert len(books) == 13
    assert len({book["id"] for book in books}) == 13
    assert "takase" not in {book["id"] for book in books}
    for book in books:
        assert 'id="book-' + book["id"] + '"' in home, book["title"]
    assert home.count('href="' + CONFIG['app_store_url'] + '"') >= 2
    assert '217枚' in home and '1.3.0' in home and '公開をお待ちください' in home
    for book in books:
        assert (OUT / "assets/covers" / (book["id"] + ".jpg")).is_file()
    assert (OUT / ".nojekyll").is_file()
    sitemap = ET.parse(OUT / "sitemap.xml")
    urls = [node.text for node in sitemap.findall(".//{*}loc")]
    assert sorted(urls) == sorted(BASE + slug for slug in ("", "support/", "privacy/", "sources/"))
    if CONFIG["contact"]["provider"] == "github":
        assert "template=support.yml" in CONFIG["contact"]["url"]
        assert (ROOT / ".github/ISSUE_TEMPLATE/support.yml").is_file()
        assert "GitHubへのログインが必要" in (OUT / "support/index.html").read_text()
    print(f"OK: {len(pages)} pages, {checked} references, 13 works, sitemap and contact configuration")


if __name__ == "__main__":
    main()
