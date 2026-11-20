"""AI stages: scout (ideas) and the per-story brief -> draft -> factcheck -> edit -> package chain."""

from __future__ import annotations

import json
import sys

from . import config, llm, rss, store
from .gate import write_gate_checklist


# ---------- scout ----------

def _ideas_path():
    return config.data_dir() / "ideas.jsonl"


def load_ideas() -> list[dict]:
    p = _ideas_path()
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def save_ideas(ideas: list[dict]) -> None:
    p = _ideas_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in ideas), encoding="utf-8")


def _performance() -> dict:
    p = config.data_dir() / "performance.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def score(idea: dict, weights: dict, perf: dict) -> float:
    niche_perf = perf.get("by_niche", {}).get(idea.get("niche", ""), {}).get("score", 0.5)
    return round(
        weights["fit"] * float(idea.get("fit", 0))
        + weights["demand"] * float(idea.get("demand", 0))
        + weights["gap"] * float(idea.get("gap", 0))
        + weights["performance"] * float(niche_perf),
        4,
    )


def scout() -> list[dict]:
    cfg = config.settings()
    sc = cfg["scout"]
    titles: list[str] = []
    for niche in cfg["niches"]:
        for tag in niche["tags"]:
            try:
                items = rss.fetch(rss.tag_feed(tag))[: sc["rss_items_per_tag"]]
                titles += [f"[{tag}] {i.title}" for i in items]
            except Exception as e:  # a dead tag feed should not stop the run
                print(f"warn: tag feed {tag}: {e}", file=sys.stderr)

    existing = load_ideas()
    used = [i["title"] for i in existing] + [s.idea.get("title", "") for s in store.all_stories()]
    perf = _performance()
    reply = llm.run(
        config.prompt(
            "scout",
            count=sc["ideas_per_run"],
            niches="\n".join(f"- {n['name']} (tags: {', '.join(n['tags'])})" for n in cfg["niches"]),
            feed_titles="\n".join(titles) or "(none fetched)",
            performance=json.dumps(perf.get("by_niche", {}), indent=2) or "{}",
            used="\n".join(f"- {t}" for t in used) or "(none)",
        ),
        stage="scout",
        web=True,
    )
    new = llm.extract_json(reply).get("ideas", [])
    for idea in new:
        idea["score"] = score(idea, sc["weights"], perf)
        idea["status"] = "new"
    ideas = sorted(existing + new, key=lambda i: i.get("score", 0), reverse=True)
    save_ideas(ideas)
    return new


def pick_idea(index: int | None = None) -> dict:
    ideas = load_ideas()
    fresh = [i for i in ideas if i.get("status") == "new"]
    if not fresh:
        raise SystemExit("no unused ideas; run `medium scout` first")
    idea = fresh[index] if index is not None else fresh[0]
    idea["status"] = "used"
    save_ideas(ideas)
    return idea


# ---------- per-story chain ----------

def _story_cfg() -> dict:
    s = config.settings()["story"]
    return {
        "min_words": s["target_words"][0],
        "max_words": s["target_words"][1],
        "min_slots": s["human_slots"][0],
        "max_slots": s["human_slots"][1],
        "tags": s["tags"],
    }


def run_stage(story: store.Story, stage: str) -> None:
    c = _story_cfg()
    if stage == "brief":
        out = llm.run(config.prompt("brief", idea=json.dumps(story.idea, indent=2), **c), stage=stage)
        story.write("brief.md", out)
    elif stage == "draft":
        out = llm.run(config.prompt("draft", brief=story.read("brief.md"), **c), stage=stage)
        story.write("draft.md", out)
    elif stage == "factcheck":
        out = llm.run(config.prompt("factcheck", draft=story.read("draft.md")), stage=stage, web=True)
        story.write("factcheck.md", out)
    elif stage == "edit":
        out = llm.run(
            config.prompt("edit", draft=story.read("draft.md"), factcheck=story.read("factcheck.md"), **c),
            stage=stage,
        )
        story.write("edited.md", out)
    elif stage == "package":
        meta = llm.extract_json(llm.run(
            config.prompt("package", brief=story.read("brief.md"), edited=story.read("edited.md"), **c),
            stage=stage,
        ))
        story.write("package/meta.json", json.dumps(meta, indent=2, ensure_ascii=False))
        story.write("package/story.md", story.read("edited.md"))
        write_gate_checklist(story, meta)
    else:
        raise ValueError(f"unknown stage {stage}")
    story.advance(stage)


def run_to_gate(story: store.Story) -> store.Story:
    while (stage := story.next_stage()) is not None:
        print(f"{story.id}: {stage}...")
        run_stage(story, stage)
    if story.state == "package":
        story.advance("awaiting_human", "ready for human gate")
    return story


def run_all() -> None:
    cad = config.settings()["cadence"]
    stories = store.all_stories()
    waiting = sum(1 for s in stories if s.state == "awaiting_human")
    for s in stories:
        if s.state not in ("awaiting_human", "published"):
            run_to_gate(s)
            waiting += 1
    while waiting < cad["max_waiting_at_gate"]:
        try:
            idea = pick_idea()
        except SystemExit:
            break
        run_to_gate(store.create(idea))
        waiting += 1
