"""Post-publish tracking: confirm stories via the author RSS feed and ingest earnings exports.

Medium has no stats API. Drop CSV exports/copies of your stats into data/earnings/
with at least these columns: url, earnings_usd (extra columns such as reads,
member_reading_minutes are kept). The rollup feeds scout's performance weight.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict

from . import config, rss, store


def confirm_published() -> list[str]:
    handle = config.settings()["author"].get("medium_handle")
    if not handle:
        return []
    live = {i.link for i in rss.fetch(rss.author_feed(handle))}
    missing = []
    for s in store.all_stories():
        if s.state == "published" and s.url and s.url.split("?")[0] not in live:
            missing.append(s.id)  # RSS only lists recent posts, so this is a hint, not an error
    return missing


def ingest_earnings() -> dict:
    rows: dict[str, dict] = {}
    for path in sorted((config.data_dir() / "earnings").glob("*.csv")):
        with open(path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                url = (row.get("url") or "").split("?")[0]
                if url:
                    rows[url] = row  # later files win
    by_url = {s.url.split("?")[0]: s for s in store.all_stories() if s.url}

    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    stories = {}
    for url, row in rows.items():
        s = by_url.get(url)
        if not s:
            continue
        earned = float(row.get("earnings_usd") or 0)
        niche = s.idea.get("niche", "unknown")
        totals[niche] += earned
        counts[niche] += 1
        stories[s.id] = {"niche": niche, **row}

    best = max((totals[n] / counts[n] for n in totals), default=0) or 1
    perf = {
        "by_niche": {
            n: {"stories": counts[n], "earnings_usd": round(totals[n], 2),
                "score": round((totals[n] / counts[n]) / best, 3)}
            for n in totals
        },
        "stories": stories,
    }
    out = config.data_dir() / "performance.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(perf, indent=2), encoding="utf-8")
    return perf
