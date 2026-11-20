import json
import shutil
from pathlib import Path

import pytest

from medium_engine import config, gate, llm, rss, stages, store

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for d in ("config", "prompts"):
        shutil.copytree(REPO / d, tmp_path / d)
    monkeypatch.setenv("MEDIUM_ROOT", str(tmp_path))
    config.settings.cache_clear()
    yield tmp_path
    config.settings.cache_clear()


def test_story_state_machine(repo):
    s = store.create({"title": "Hello, World! Internships"})
    assert s.id.endswith("hello-world-internships")
    assert s.next_stage() == "brief"
    for stage in store.AI_STAGES:
        s.advance(stage)
    assert s.next_stage() is None
    assert store.load(s.id).state == "package"


def test_gate_refuses_placeholders_and_light_edits(repo):
    s = store.create({"title": "x"})
    ai = "# T\n\nSome text here. [[HUMAN: your story]]\n" * 5
    s.write("package/story.md", ai)
    s.advance("awaiting_human")
    s.write("package/final.md", ai)
    problems = gate.check(s)
    assert any("slot" in p for p in problems)
    assert any("edit ratio" in p for p in problems)

    s.write("package/final.md", "# Mine\n\nI rewrote all of this from my own experience at length.\n" * 3)
    assert gate.check(s) == []
    gate.done(s, "https://medium.com/@me/mine-123")
    assert store.load(s.id).state == "published"


def test_extract_json_handles_fences():
    assert llm.extract_json('blah\n```json\n{"a": 1}\n```') == {"a": 1}
    assert llm.extract_json('prefix {"ideas": []} suffix') == {"ideas": []}


def test_prompt_render_keeps_json_braces(repo):
    text = config.prompt("package", brief="B", edited="E", tags=5)
    assert '{"title"' in text and "exactly 5 tags" in text


def test_score_weights(repo):
    w = config.settings()["scout"]["weights"]
    s = stages.score({"fit": 1, "demand": 1, "gap": 1, "niche": "n"}, w, {})
    assert 0 < s <= 1


def test_rss_parse():
    xml = b"""<rss><channel><item><title>T</title><link>https://medium.com/p/1?source=rss</link>
    <pubDate>Mon</pubDate><category>a</category></item></channel></rss>"""
    [item] = rss.parse(xml)
    assert item.link == "https://medium.com/p/1" and item.categories == ["a"]
