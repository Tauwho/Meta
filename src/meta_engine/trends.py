"""Trend signals: Google Trends Vietnam and shared Vietnamese news RSS, plus each account's own feeds (RSS or Atom)."""

from __future__ import annotations

import sys
import urllib.request
import xml.etree.ElementTree as ET

from . import config, threads

UA = {"User-Agent": "Mozilla/5.0 (meta-engine trend reader)"}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse(xml_bytes: bytes, source: str, limit: int) -> list[dict]:
    """RSS items or Atom entries -> [{source, title, link, traffic?, related?}]. Handles Google Trends' ht: fields."""
    out = []
    for item in (e for e in ET.fromstring(xml_bytes).iter() if _local(e.tag) in ("item", "entry")):
        sig = {"source": source}
        related = []
        for child in item.iter():
            name, text = _local(child.tag), (child.text or "").strip()
            if name == "title" and "title" not in sig:
                sig["title"] = text
            elif name == "link" and "link" not in sig and (text or child.get("href")):
                sig["link"] = text or child.get("href")  # Atom puts the URL in href
            elif name == "approx_traffic":
                sig["traffic"] = text
            elif name == "news_item_title":
                related.append(text)
        if related:
            sig["related"] = related[:2]
        if sig.get("title"):
            out.append(sig)
        if len(out) >= limit:
            break
    return out


def _fetch(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return r.read()


def collect(account: str) -> list[dict]:
    """Shared signals plus the account's niche feeds; a dead feed is skipped with a warning, never fatal."""
    cfg, acc = config.settings()["trends"], config.settings()["accounts"][account]
    shared = acc.get("shared_feeds", True)  # false: only the account's own feeds (e.g. global news, no VN trends)
    feeds = (cfg["feeds"] if shared else []) + acc.get("feeds", [])
    sources = [("google_trends_vn", cfg["google_trends"], 20)] if shared else []
    sources += [(u.split("//")[1].split(".rss")[0], u, cfg.get("per_feed", 8)) for u in feeds]
    signals = []
    for name, url, limit in sources:
        try:
            signals += parse(_fetch(url), name, limit)
        except Exception as e:  # network/XML errors: trends are best-effort input
            print(f"warning: trend feed {name} skipped: {e}", file=sys.stderr)
    return signals + threads_posts(account)


def threads_posts(account: str) -> list[dict]:
    """Popular Threads posts for the account's search keywords: candidates to quote. Own posts dropped."""
    acc = config.settings()["accounts"][account]
    out, seen = [], set()
    for q in acc.get("search_keywords", []):
        try:
            found = threads.search(account, q)
        except SystemExit as e:  # no token, no permission, rate limit: quoting is optional
            print(f"warning: threads search {q!r} skipped: {e}", file=sys.stderr)
            continue
        for p in found:
            if p.get("username") == acc.get("handle") or not p.get("text") or p["id"] in seen:
                continue
            seen.add(p["id"])
            out.append({"source": f"threads @{p.get('username', '?')}", "title": " ".join(p["text"].split())[:200],
                        "link": p.get("permalink", ""), "quote_id": p["id"]})
    return out


def render(signals: list[dict]) -> str:
    lines = []
    for s in signals:
        extra = f" [{s['traffic']} searches]" if s.get("traffic") else ""
        rel = f" | news: {'; '.join(s['related'])}" if s.get("related") else ""
        quote = f" [quote_post_id {s['quote_id']}]" if s.get("quote_id") else ""
        lines.append(f"- ({s['source']}) {s['title']}{extra}{rel}{quote} {s.get('link', '')}".rstrip())
    return "\n".join(lines) or "(no feed reachable; find today's trends for this persona with web search)"
