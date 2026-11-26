"""Trend signals for Vietnam: Google Trends daily RSS plus Vietnamese news RSS headlines."""

from __future__ import annotations

import sys
import urllib.request
import xml.etree.ElementTree as ET

from . import config

UA = {"User-Agent": "Mozilla/5.0 (meta-engine trend reader)"}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse(xml_bytes: bytes, source: str, limit: int) -> list[dict]:
    """RSS items -> [{source, title, link, traffic?, related?}]. Handles Google Trends' ht: fields."""
    out = []
    for item in ET.fromstring(xml_bytes).iter("item"):
        sig = {"source": source}
        related = []
        for child in item.iter():
            name, text = _local(child.tag), (child.text or "").strip()
            if name == "title" and "title" not in sig:
                sig["title"] = text
            elif name == "link" and "link" not in sig:
                sig["link"] = text
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


def collect() -> list[dict]:
    """All signals; a dead feed is skipped with a warning, never fatal."""
    cfg = config.settings()["trends"]
    sources = [("google_trends_vn", cfg["google_trends"], 20)]
    sources += [(u.split("//")[1].split("/")[0], u, cfg.get("per_feed", 8)) for u in cfg["feeds"]]
    signals = []
    for name, url, limit in sources:
        try:
            signals += parse(_fetch(url), name, limit)
        except Exception as e:  # network/XML errors: trends are best-effort input
            print(f"warning: trend feed {name} skipped: {e}", file=sys.stderr)
    return signals


def render(signals: list[dict]) -> str:
    lines = []
    for s in signals:
        extra = f" [{s['traffic']} searches]" if s.get("traffic") else ""
        rel = f" | news: {'; '.join(s['related'])}" if s.get("related") else ""
        lines.append(f"- ({s['source']}) {s['title']}{extra}{rel} {s.get('link', '')}".rstrip())
    return "\n".join(lines) or "(no feed reachable; find today's Vietnamese trends with web search)"
