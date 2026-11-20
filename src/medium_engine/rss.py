"""Read-only access to Medium's public RSS feeds (the only automated Medium access we use)."""

from __future__ import annotations

import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass

USER_AGENT = "medium-engine/0.1 (+rss reader)"


@dataclass
class FeedItem:
    title: str
    link: str
    published: str
    categories: list[str]


def fetch(url: str, timeout: int = 20) -> list[FeedItem]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return parse(resp.read())


def parse(xml_bytes: bytes) -> list[FeedItem]:
    root = ET.fromstring(xml_bytes)
    items = []
    for it in root.iter("item"):
        items.append(FeedItem(
            title=(it.findtext("title") or "").strip(),
            link=(it.findtext("link") or "").split("?")[0].strip(),
            published=(it.findtext("pubDate") or "").strip(),
            categories=[c.text or "" for c in it.findall("category")],
        ))
    return items


def tag_feed(tag: str) -> str:
    return f"https://medium.com/feed/tag/{tag}"


def author_feed(handle: str) -> str:
    return f"https://medium.com/feed/@{handle.lstrip('@')}"
