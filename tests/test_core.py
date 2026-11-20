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


def test_agent_protocol_walks_story_to_gate(repo, monkeypatch):
    import json as _json
    from medium_engine import agent
    monkeypatch.setattr(stages.rss, "fetch", lambda url: [])
    (repo / "config" / "pipeline.yaml").write_text(
        (repo / "config" / "pipeline.yaml").read_text(encoding="utf-8").replace("max_revisions: 2", "max_revisions: 1"),
        encoding="utf-8")
    config.settings.cache_clear()
    outputs = {
        "scout": _json.dumps({"ideas": [{"title": "Saying no is the productivity system nobody sells you",
                                          "niche": "CS student life and study systems",
                                          "fit": 0.9, "demand": 0.7, "gap": 0.6}]}),
        "brief": "## Reader\nStudents.", "draft": GOOD, "factcheck": "| # |\n## Must fix\nNone",
        "edit": GOOD, "revise": GOOD,
        "review": _json.dumps({"scores": {k: 3 for k in stages.CRITERIA}, "fixes": [], "verdict": "ok"}),
        "package": _json.dumps({"title": "Saying no is the productivity system nobody sells you",
                                "subtitle": "s", "tags": ["a"], "publication": {"name": "P"},
                                "cover_image": {"unsplash_query": "q"}}),
    }
    seen = []
    for _ in range(20):
        t = agent.next_ticket()
        if t["done"]:
            break
        seen.append(t["stage"])
        assert "house_style" in open(t["system_file"], encoding="utf-8").read()
        open(t["output_file"], "w", encoding="utf-8").write(outputs[t["stage"]])
        agent.submit(t["job_id"])
        if len(store.all_stories()) and all(s.state == "awaiting_human" for s in store.all_stories()):
            break
    assert seen == ["scout", "brief", "draft", "factcheck", "edit", "review", "revise", "review", "package"]
    [s] = store.all_stories()
    assert s.state == "awaiting_human"
    assert s.path("GATE.md").exists() and s.path("package/cover.png").exists()
    assert _json.loads(s.read("review.json"))["passed"] is False


def test_submit_rejects_bad_json_and_keeps_job_open(repo, monkeypatch):
    from medium_engine import agent
    monkeypatch.setattr(stages.rss, "fetch", lambda url: [])
    t = agent.next_ticket()
    assert t["stage"] == "scout"
    open(t["output_file"], "w", encoding="utf-8").write("not json")
    with pytest.raises(Exception):
        agent.submit(t["job_id"])
    assert agent.next_ticket()["job_id"] == t["job_id"]


def test_lint_length_counts_slots_and_flags_invented_opening(repo):
    from medium_engine import lint
    body = "# A title that is long enough to pass the check\n\n*sub*\n\nPicture a student at a desk.\n\n" \
        + "## Section\n\n" + ("This is a plain sentence with exactly ten words in it. " * 10 + "\n\n") * 5
    rules = {i.rule for i in lint.lint(body).issues}
    assert "length" in rules and "opening" in rules
    with_slots = body + "\n\n" + "\n\n".join("[[HUMAN: x]]" for _ in range(5))
    assert "length" not in {i.rule for i in lint.lint(with_slots).issues}


def test_review_stops_on_plateau(repo):
    import json as _json
    s = store.create({"title": "x"})
    for st in ("brief", "draft", "factcheck", "edit"):
        s.write({"brief": "brief.md", "draft": "draft.md", "factcheck": "factcheck.md", "edit": "edited.md"}[st], GOOD)
        s.advance(st)
    flat = _json.dumps({"scores": {k: 3 for k in stages.CRITERIA}, "fixes": []})
    for expected in ("review", "revise", "review"):
        job = stages.story_job(store.load(s.id))
        assert job.stage == expected
        stages.apply(job, flat if expected == "review" else GOOD)
    job = stages.story_job(store.load(s.id))   # max_revisions is 2, but no gain -> package
    assert job.stage == "package"
