"""AI work as discrete jobs: build a prompt, get text back, apply it.

Both backends share this module:
- `api`   : llm.run() executes each job against the Claude API (needs a key).
- `agent` : `medium agent next/submit` hands jobs to a Claude Code session
            (e.g. a scheduled task on a Claude subscription), which writes the output.

Story chain: brief -> draft -> factcheck -> edit -> (review <-> revise)* -> package -> awaiting_human
Global jobs: scout (when no fresh ideas), learn (after you publish).
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass

from . import config, lint, rss, store, visuals
from .gate import write_gate_checklist

CRITERIA = ["voice", "specificity", "argument", "structure", "clarity", "human_room", "boost_readiness"]


@dataclass
class Job:
    kind: str            # scout | story | learn
    stage: str           # scout | brief | draft | factcheck | edit | review | revise | package | learn
    story_id: str | None
    prompt: str
    web: bool = False
    fmt: str = "markdown"  # markdown | json

    @property
    def effort_key(self) -> str:
        return {"revise": "edit", "learn": "edit"}.get(self.stage, self.stage)

    def describe(self) -> dict:
        d = asdict(self)
        d.pop("prompt")
        return d


# ---------- ideas ----------

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


def fresh_ideas() -> list[dict]:
    return [i for i in load_ideas() if i.get("status") == "new"]


def pick_idea(index: int | None = None) -> dict:
    ideas = load_ideas()
    fresh = [i for i in ideas if i.get("status") == "new"]
    if not fresh:
        raise SystemExit("no unused ideas; run scout first")
    idea = fresh[index] if index is not None else fresh[0]
    idea["status"] = "used"
    save_ideas(ideas)
    return idea


def scout_job() -> Job:
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
    used = [i["title"] for i in load_ideas()] + [s.idea.get("title", "") for s in store.all_stories()]
    prompt = config.prompt(
        "scout",
        count=sc["ideas_per_run"],
        niches="\n".join(f"- {n['name']} (tags: {', '.join(n['tags'])})" for n in cfg["niches"]),
        feed_titles="\n".join(titles) or "(none fetched)",
        performance=json.dumps(_performance().get("by_niche", {}), indent=2),
        used="\n".join(f"- {t}" for t in used) or "(none)",
    )
    return Job("scout", "scout", None, prompt, web=True, fmt="json")


def apply_scout(data: dict) -> list[dict]:
    sc = config.settings()["scout"]
    perf = _performance()
    new = data.get("ideas", [])
    if not new:
        raise ValueError("scout returned no ideas")
    for idea in new:
        idea["score"] = score(idea, sc["weights"], perf)
        idea["status"] = "new"
    save_ideas(sorted(load_ideas() + new, key=lambda i: i.get("score", 0), reverse=True))
    return new


# ---------- story chain ----------

def _story_cfg() -> dict:
    s = config.settings()["story"]
    return {
        "min_words": s["target_words"][0],
        "max_words": s["target_words"][1],
        "min_slots": s["human_slots"][0],
        "max_slots": s["human_slots"][1],
        "tags": s["tags"],
    }


def review_avg(review: dict) -> float:
    scores = review.get("scores", {})
    vals = [float(scores.get(k, 0)) for k in CRITERIA]
    return round(sum(vals) / len(vals), 2)


def _rounds(story: store.Story) -> list[dict]:
    if not story.path("review.json").exists():
        return []
    return json.loads(story.read("review.json")).get("rounds", [])


def _save_rounds(story: store.Story, rounds: list[dict], final: bool = False) -> None:
    out: dict = {"rounds": rounds}
    if final and rounds:
        out.update(passed=rounds[-1]["passed"], final_avg=rounds[-1]["avg"])
    story.write("review.json", json.dumps(out, indent=2, ensure_ascii=False))


def _fixes_text(review: dict) -> str:
    return "\n".join(f"- \"{f.get('where', '')}\": {f.get('problem', '')} -> {f.get('fix', '')}"
                     for f in review.get("fixes", [])) or "(none)"


def story_job(story: store.Story) -> Job | None:
    """Next AI job for this story, or None once it is at/after the gate."""
    c = _story_cfg()
    sid = story.id
    s = story.state
    if s == "idea":
        return Job("story", "brief", sid, config.prompt("brief", idea=json.dumps(story.idea, indent=2), **c))
    if s == "brief":
        return Job("story", "draft", sid, config.prompt("draft", brief=story.read("brief.md"), **c))
    if s == "draft":
        return Job("story", "factcheck", sid, config.prompt("factcheck", draft=story.read("draft.md")), web=True)
    if s == "factcheck":
        return Job("story", "edit", sid, config.prompt(
            "edit", draft=story.read("draft.md"), factcheck=story.read("factcheck.md"), **c))
    if s == "edit":
        q = config.settings()["quality"]["review"]
        rounds = _rounds(story)
        text = story.read("edited.md")
        if not rounds or rounds[-1].get("revised"):
            return Job("story", "review", sid, config.prompt(
                "review", brief=story.read("brief.md"), story=text, lint=lint.lint(text, ai=True).markdown()), fmt="json")
        last = rounds[-1]
        plateau = len(rounds) >= 2 and last["avg"] <= rounds[-2]["avg"] + q.get("min_gain", 0.1)
        if last["passed"] or last["attempt"] >= q["max_revisions"] or plateau:
            _save_rounds(story, rounds, final=True)
            story.advance("review", f"avg={last['avg']} passed={last['passed']}")
            return story_job(story)
        return Job("story", "revise", sid, config.prompt(
            "revise", story=text, fixes=_fixes_text(last), lint=lint.lint(text, ai=True).markdown(), **c))
    if s == "review":
        return Job("story", "package", sid, config.prompt(
            "package", brief=story.read("brief.md"), edited=story.read("edited.md"), **c), fmt="json")
    if s == "package":
        story.advance("awaiting_human", "ready for human gate")
    return None


def apply_story(story: store.Story, stage: str, output) -> None:
    files = {"brief": "brief.md", "draft": "draft.md", "factcheck": "factcheck.md", "edit": "edited.md"}
    if stage in files:
        story.write(files[stage], output)
        story.advance(stage)
    elif stage == "review":
        q = config.settings()["quality"]["review"]
        rounds = _rounds(story)
        rep = lint.lint(story.read("edited.md"), ai=True)
        avg = review_avg(output)
        rounds.append({"attempt": len(rounds), "avg": avg, "lint_errors": len(rep.errors),
                       "passed": avg >= q["min_score"] and rep.ok, "revised": False, **output})
        _save_rounds(story, rounds)
    elif stage == "revise":
        rounds = _rounds(story)
        story.write(f"revisions/edited.v{len(rounds) - 1}.md", story.read("edited.md"))
        story.write("edited.md", output)
        rounds[-1]["revised"] = True
        _save_rounds(story, rounds)
    elif stage == "package":
        story.write("package/meta.json", json.dumps(output, indent=2, ensure_ascii=False))
        story.write("package/story.md", story.read("edited.md"))
        try:
            visuals.cover(story, output)
        except Exception as e:  # a missing font or Pillow issue must not block the pipeline
            print(f"warn: cover not generated: {e}", file=sys.stderr)
        write_gate_checklist(story, output)
        story.advance("package")
        story.advance("awaiting_human", "ready for human gate")
    else:
        raise ValueError(f"unknown stage {stage}")


# ---------- learning from your rewrites ----------

def learn_job() -> Job | None:
    for s in store.all_stories():
        if s.state == "published" and not s.idea.get("_learned") \
                and s.path("package/final.md").exists() and s.path("package/story.md").exists():
            return Job("learn", "learn", s.id, config.prompt(
                "learn", ai=s.read("package/story.md"), final=s.read("package/final.md"), learned=config.learned()))
    return None


def apply_learn(story: store.Story, notes: str) -> None:
    (config.root() / "config" / "style-learned.md").write_text(notes.strip() + "\n", encoding="utf-8")
    story.idea["_learned"] = True
    story.save()


# ---------- scheduling ----------

def next_job() -> Job | None:
    """Pick the next job across the whole queue, respecting cadence limits."""
    if (j := learn_job()):
        return j
    stories = store.all_stories()
    for s in stories:
        if s.state not in ("awaiting_human", "published") and (j := story_job(s)):
            return j
    waiting = sum(1 for s in store.all_stories() if s.state == "awaiting_human")
    if waiting >= config.settings()["cadence"]["max_waiting_at_gate"]:
        return None
    if not fresh_ideas():
        return scout_job()
    return story_job(store.create(pick_idea()))


def parse_output(job: Job, text: str):
    from .llm import extract_json  # local import keeps the agent path free of the SDK
    text = text.strip()
    if job.fmt == "json":
        return extract_json(text)
    if not text:
        raise ValueError("empty output")
    return text


def apply(job: Job, text: str) -> None:
    out = parse_output(job, text)
    if job.kind == "scout":
        apply_scout(out)
    elif job.kind == "learn":
        apply_learn(store.load(job.story_id), out)
    else:
        story = store.load(job.story_id)
        expected = story_job(story)
        if expected is None or expected.stage != job.stage:
            raise ValueError(f"stale job: story is at '{story.state}', expected stage "
                             f"{expected.stage if expected else None}, got {job.stage}")
        apply_story(story, job.stage, out)


# ---------- API backend ----------

def execute(job: Job) -> None:
    from . import llm
    print(f"{job.story_id or '-'}: {job.stage}...")
    apply(job, llm.run(job.prompt, stage=job.effort_key, web=job.web))


def run_to_gate(story: store.Story) -> store.Story:
    while (job := story_job(story)) is not None:
        execute(job)
        story = store.load(story.id)
    return story


def run_all(max_jobs: int = 40) -> int:
    n = 0
    while n < max_jobs and (job := next_job()) is not None:
        execute(job)
        n += 1
    return n
