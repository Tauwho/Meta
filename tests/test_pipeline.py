import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from meta_engine import agent, config, posts, trends

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo(tmp_path, monkeypatch):
    shutil.copytree(REPO / "config", tmp_path / "config")
    shutil.copytree(REPO / "prompts", tmp_path / "prompts")
    monkeypatch.setenv("META_ROOT", str(tmp_path))
    config.settings.cache_clear()
    config.settings()["publish"]["require_approval"] = True  # tests pin these; real config may differ
    config.settings()["accounts"]["A"]["active"] = True
    config.settings()["cadence"].update(post_hours_vn=[7, 23], min_gap_minutes=120)
    monkeypatch.setattr(trends, "collect", lambda account: [{"source": "t", "title": "Hoa hậu Hoàn vũ 2026"}])
    yield tmp_path
    config.settings.cache_clear()


def draft(**kw):
    base = {"topic": "Hoa hậu", "category": "showbiz", "why_now": "trend",
            "text": "Hook line\nChi tiết. Bạn nghĩ sao?", "reply": "Nguồn: VnExpress",
            "sources": ["https://vnexpress.net/x"]}
    return {**base, **kw}


GT = b"""<rss xmlns:ht="https://trends.google.com/trending/rss"><channel><title>Daily</title>
<item><title>vnindex</title><ht:approx_traffic>2000+</ht:approx_traffic><link>https://t</link>
<ht:news_item><ht:news_item_title>VN-Index tang</ht:news_item_title></ht:news_item></item>
<item><title>thoi tiet</title></item></channel></rss>"""


def test_trends_parse_reads_google_trends_fields_and_limit():
    sig = trends.parse(GT, "gt", limit=1)
    assert sig == [{"source": "gt", "title": "vnindex", "traffic": "2000+", "link": "https://t",
                    "related": ["VN-Index tang"]}]
    assert "[2000+ searches]" in trends.render(sig)


def test_add_drafts_validates_and_dedupes(repo):
    with pytest.raises(ValueError, match="500"):
        posts.add_drafts("A", {"posts": [draft(text="x" * 501)]})
    with pytest.raises(ValueError, match="link"):
        posts.add_drafts("A", {"posts": [draft(text="see https://x")]})
    with pytest.raises(ValueError, match="sources"):
        posts.add_drafts("A", {"posts": [draft(sources=[])]})
    assert posts.add_drafts("A", {"posts": [draft(topic="take", kind="take", sources=[], reply="")]})
    assert len(posts.add_drafts("A", {"posts": [draft(), draft(topic="HOA  HẬU")]})) == 1
    assert posts.add_drafts("A", {"posts": [draft()]}) == []  # topic covered recently


def test_review_moves_drafts_by_score_and_approval_setting(repo):
    a, b, c = posts.add_drafts("A", {"posts": [draft(topic="a"), draft(topic="b"), draft(topic="c")]})
    counts = posts.apply_reviews({"reviews": [
        {"id": a, "verdict": "pass", "score": 8},
        {"id": b, "verdict": "fix", "score": 9, "text": "Mới hơn?"},
        {"id": c, "verdict": "pass", "score": 5}]})
    assert counts == {"pending": 2, "rejected": 1}
    by_id = {p["id"]: p for p in posts.load()}
    assert by_id[b]["text"] == "Mới hơn?"


def test_due_respects_window_gap_and_order(repo):
    at = datetime(2026, 11, 27, 5, 0, tzinfo=timezone.utc)  # 12:00 in Vietnam
    ps = [{"id": "2", "account": "A", "state": "approved", "created": "2026-11-27T02:00:00+00:00"},
          {"id": "1", "account": "A", "state": "approved", "created": "2026-11-27T01:00:00+00:00"}]
    assert posts.due(ps, "A", at)["id"] == "1"
    assert posts.due(ps, "A", at.replace(hour=17)) is None  # 00:00 in Vietnam
    ps.append({"id": "0", "account": "A", "state": "published", "created": "x",
               "published_at": posts.iso(at - timedelta(minutes=30))})
    assert posts.due(ps, "A", at) is None
    assert posts.due(ps, "A", at, ignore_gap=True)["id"] == "1"


def test_agent_round_trip_write_then_review(repo):
    t = agent.next_ticket()
    assert t["stage"] == "write" and "Hoa hậu Hoàn vũ 2026" in Path(t["prompt_file"]).read_text(encoding="utf-8")
    Path(t["output_file"]).write_text(json.dumps({"posts": [draft()]}, ensure_ascii=False), encoding="utf-8")
    assert agent.submit(t["job_id"]) == "write A: 1 draft(s) added"
    r = agent.next_ticket()
    assert r["stage"] == "review"
    pid = posts.load()[0]["id"]
    Path(r["output_file"]).write_text(json.dumps({"reviews": [{"id": pid, "verdict": "pass", "score": 8}]}))
    assert agent.submit(r["job_id"]) == "review A: 1 pending"


def test_review_skips_gate_when_approval_off(repo):
    config.settings()["publish"]["require_approval"] = False
    (a,) = posts.add_drafts("A", {"posts": [draft()]})
    assert posts.apply_reviews({"reviews": [{"id": a, "verdict": "pass", "score": 8}]}) == {"approved": 1}


def test_card_length_is_validated_and_stored(repo):
    with pytest.raises(ValueError, match="card"):
        posts.add_drafts("A", {"posts": [draft(card="x" * 161)]})
    (pid,) = posts.add_drafts("A", {"posts": [draft(card="Ai cũng từng chờ tin nhắn tới sáng")]})
    assert posts.load()[0]["card"] == "Ai cũng từng chờ tin nhắn tới sáng"


def test_card_renders_4x5_png(tmp_path):
    from PIL import Image
    from meta_engine import card
    out = card.render("Yêu xa 2 năm mà chưa từng nói chuyện tương lai? " * 3, "goycoon", tmp_path / "c.png", seed="x")
    assert Image.open(out).size == (1080, 1350)
