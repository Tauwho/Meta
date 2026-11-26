"""Post queue on disk (data/posts.jsonl) and its state machine.

draft -> (review) -> pending (needs `meta approve`) | approved | rejected
approved -> published | expired
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta

from . import config

MAX_CHARS = 500  # Threads hard limit per post
STATES = ["draft", "pending", "approved", "rejected", "published", "expired"]


def _path():
    return config.data_dir() / "posts.jsonl"


def load() -> list[dict]:
    p = _path()
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def save(posts: list[dict]) -> None:
    _path().write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in posts), encoding="utf-8")


def find(posts: list[dict], post_id: str) -> dict:
    for p in posts:
        if p["id"] == post_id:
            return p
    raise SystemExit(f"no post {post_id}")


def _ts(p: dict, key: str) -> datetime:
    return datetime.fromisoformat(p[key])


def iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


# ---------- validation ----------

def parse_json(text: str) -> dict:
    """Agent output -> dict; tolerates a ```json fence around it."""
    text = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text.strip())
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("output must be a JSON object")
    return data


def check_text(text: str, field: str = "text") -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"{field} is empty")
    text = text.strip()
    if len(text) > MAX_CHARS:
        raise ValueError(f"{field} is {len(text)} chars; Threads allows {MAX_CHARS}")
    return text


def _norm(topic: str) -> str:
    return re.sub(r"\s+", " ", topic.casefold()).strip()


def recent_topics(posts: list[dict], account: str, days: int = 14) -> set[str]:
    cutoff = config.now() - timedelta(days=days)
    return {_norm(p["topic"]) for p in posts
            if p["account"] == account and p["state"] != "rejected" and _ts(p, "created") > cutoff}


def add_drafts(account: str, data: dict) -> list[str]:
    """Validate a write-job output and append its posts as drafts. Raises ValueError on bad output."""
    items = data.get("posts")
    if not isinstance(items, list) or not items:
        raise ValueError('expected {"posts": [...]} with at least one post')
    posts = load()
    seen = recent_topics(posts, account)
    stamp = config.now()
    added = []
    for i, it in enumerate(items):
        topic = str(it.get("topic", "")).strip()
        if not topic:
            raise ValueError(f"posts[{i}].topic is empty")
        text = check_text(it.get("text"), f"posts[{i}].text")
        if "http" in text:
            raise ValueError(f"posts[{i}].text has a link; put sources in reply")
        reply = check_text(it["reply"], f"posts[{i}].reply") if it.get("reply") else ""
        sources = [s for s in it.get("sources", []) if isinstance(s, str) and s.startswith("http")]
        if not sources:
            raise ValueError(f"posts[{i}].sources needs at least one URL")
        if _norm(topic) in seen:
            continue  # already covered this topic recently; drop silently
        seen.add(_norm(topic))
        pid = f"{stamp.strftime('%Y%m%dT%H%M%S')}-{account}{i}"
        posts.append({
            "id": pid, "account": account, "state": "draft", "created": iso(stamp),
            "topic": topic, "category": str(it.get("category", "")), "why_now": str(it.get("why_now", "")),
            "text": text, "reply": reply, "sources": sources,
        })
        added.append(pid)
    save(posts)
    return added


def apply_reviews(data: dict) -> dict:
    """Validate a review-job output and move each draft on. Returns counts by new state."""
    items = data.get("reviews")
    if not isinstance(items, list) or not items:
        raise ValueError('expected {"reviews": [...]}')
    posts = load()
    min_score = config.settings()["review"]["min_score"]
    ok_state = "pending" if config.settings()["publish"]["require_approval"] else "approved"
    counts: dict[str, int] = {}
    for i, r in enumerate(items):
        p = find(posts, str(r.get("id")))
        if p["state"] != "draft":
            continue
        verdict = r.get("verdict")
        if verdict not in ("pass", "fix", "reject"):
            raise ValueError(f"reviews[{i}].verdict must be pass|fix|reject")
        score = int(r.get("score", 0))
        if verdict == "fix":
            p["text"] = check_text(r.get("text"), f"reviews[{i}].text")
            if "http" in p["text"]:
                raise ValueError(f"reviews[{i}].text has a link")
            if r.get("reply"):
                p["reply"] = check_text(r["reply"], f"reviews[{i}].reply")
        p["review"] = {"verdict": verdict, "score": score, "reason": str(r.get("reason", ""))}
        p["state"] = "rejected" if verdict == "reject" or score < min_score else ok_state
        counts[p["state"]] = counts.get(p["state"], 0) + 1
    save(posts)
    return counts


# ---------- publishing choice ----------

def expire_stale(posts: list[dict]) -> int:
    cutoff = config.now() - timedelta(hours=config.settings()["cadence"]["max_age_hours"])
    n = 0
    for p in posts:
        if p["state"] in ("pending", "approved") and _ts(p, "created") < cutoff:
            p["state"] = "expired"
            n += 1
    return n


def due(posts: list[dict], account: str, at: datetime) -> dict | None:
    """Oldest approved post for the account, if the posting window and gap allow one now."""
    cad = config.settings()["cadence"]
    start, end = cad["post_hours_vn"]
    if not start <= at.astimezone(config.VN).hour < end:
        return None
    published = [p for p in posts if p["account"] == account and p["state"] == "published"]
    if published:
        last = max(_ts(p, "published_at") for p in published)
        if at - last < timedelta(minutes=cad["min_gap_minutes"]):
            return None
    ready = [p for p in posts if p["account"] == account and p["state"] == "approved"]
    return min(ready, key=lambda p: p["created"]) if ready else None
