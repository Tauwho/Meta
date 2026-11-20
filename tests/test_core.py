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

    s.write("package/final.md", "# Mine\n\n" + "I rewrote all of this from my own experience at length.\n\n" * 3)
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


GOOD = """# Saying no is the productivity system nobody sells you

*Most calendars are full of work that should never have been accepted, and no app can fix that part.*

## The real problem

I used to think my week was badly organised. It was not. It was overcommitted, and those are different problems.

A better system helps you do the right work faster. It does nothing about work you should not be doing at all.

## What changed

[[HUMAN: the week you cut three commitments and what happened]]

The useful question is not how to get more done. It is what would make the rest unnecessary.
"""


def test_lint_clean_story_has_no_errors(repo):
    from medium_engine import lint
    rep = lint.lint(GOOD)
    assert rep.ok, [str(i) for i in rep.errors]
    assert rep.stats["placeholders"] == 1 and rep.stats["sections"] == 2


def test_lint_catches_banned_heading_and_voice_phrases(repo):
    from medium_engine import lint
    (repo / "config" / "voice.md").write_text('## Never\n- "secret sauce"\n', encoding="utf-8")
    bad = GOOD + "\n#### Deep heading\n\nLet's delve into the secret sauce. The color is very nice.\n"
    rules = {(i.level, i.rule) for i in lint.lint(bad).issues}
    assert ("error", "banned-phrase") in rules
    assert ("error", "heading-level") in rules
    assert ("warn", "spelling") in rules
    assert any("secret sauce" in str(i) for i in lint.lint(bad).errors)


def test_review_average():
    from medium_engine import stages
    assert stages.review_avg({"scores": {k: 4 for k in stages.CRITERIA}}) == 4.0


def test_cover_and_export(repo):
    from medium_engine import visuals
    s = store.create({"title": "Saying no is the productivity system nobody sells you",
                      "niche": "CS student life and study systems"})
    out = visuals.cover(s)
    from PIL import Image
    assert Image.open(out).size == (1400, 788)
    s.write("package/final.md", GOOD)
    html = visuals.export_html(s).read_text(encoding="utf-8")
    assert "<h2>The real problem</h2>" in html


def test_gate_done_saves_exemplar(repo):
    s = store.create({"title": "x"})
    s.write("package/story.md", "# Draft title that is long enough for lint\n\nAI text [[HUMAN: x]]\n" * 3)
    s.advance("awaiting_human")
    s.write("package/final.md", GOOD.replace("[[HUMAN: the week you cut three commitments and what happened]]",
                                             "In March I dropped two clubs and a side project."))
    gate.done(s, "https://medium.com/@me/x")
    assert (repo / "config" / "exemplars" / f"{s.id}.md").exists()
