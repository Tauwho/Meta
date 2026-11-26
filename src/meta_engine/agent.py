"""Agent backend: a Claude Code session (scheduled task on a Claude subscription) is the model.

Protocol, one job at a time:
  meta agent next          -> prints a JSON job ticket, writes jobs/<id>.prompt.md + jobs/system.md
  (session writes its JSON answer to the ticket's output_file)
  meta agent submit <id>   -> validates + applies the output
Repeat until `next` prints {"done": true}.

Jobs: review (drafts waiting) first, then write (an active account's queue is below target).
"""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from . import config, posts, trends


def jobs_dir() -> Path:
    d = config.root() / "jobs"
    d.mkdir(exist_ok=True)
    return d


def _recent(all_posts: list[dict], account: str) -> str:
    cutoff = config.now() - timedelta(days=14)
    rows = [p for p in all_posts if p["account"] == account and p["state"] != "rejected"
            and posts._ts(p, "created") > cutoff]
    return "\n".join(f"- [{p['state']}] {p['topic']}" for p in rows[-40:]) or "(none yet)"


def _performance(all_posts: list[dict], account: str) -> str:
    done = [p for p in all_posts if p["account"] == account and p.get("insights")]
    if not done:
        return "(no published posts with insights yet)"
    done.sort(key=lambda p: p["insights"].get("views", 0), reverse=True)

    def row(p):
        i = p["insights"]
        return (f"- {i.get('views', 0)} views, {i.get('likes', 0)} likes, {i.get('replies', 0)} replies "
                f"| {p['category']} | {p['text'][:90]!r}")
    top, bottom = done[:5], done[-5:] if len(done) > 5 else []
    return "Best:\n" + "\n".join(map(row, top)) + ("\nWorst:\n" + "\n".join(map(row, bottom)) if bottom else "")


def plan() -> dict | None:
    """The next job as {stage, account, prompt, web}, or None."""
    all_posts = posts.load()
    if posts.expire_stale(all_posts):
        posts.save(all_posts)
    drafts = [p for p in all_posts if p["state"] == "draft"]
    if drafts:
        account = drafts[0]["account"]
        batch = [p for p in drafts if p["account"] == account]
        acc = config.settings()["accounts"][account]
        view = [{k: p.get(k, "") for k in ("id", "topic", "kind", "category", "why_now", "text", "card", "reply", "topic_tag", "poll", "quote_post_id", "sources")}
                for p in batch]
        return {"stage": "review", "account": account, "web": True, "prompt": config.prompt(
            "review", account=account, persona=acc["persona"], min_score=config.settings()["review"]["min_score"],
            drafts=json.dumps(view, ensure_ascii=False, indent=2), recent=_recent(all_posts, account))}
    cad = config.settings()["cadence"]
    def ready_count(account):
        return sum(1 for p in all_posts if p["account"] == account and p["state"] in ("pending", "approved"))

    # emptiest queue first, so one account never starves the others within a run's job limit
    for account, acc in sorted(config.active_accounts().items(), key=lambda kv: ready_count(kv[0])):
        ready = ready_count(account)
        if ready >= cad["queue_target"]:
            continue
        n = min(cad["write_batch"], cad["queue_target"] - ready)
        return {"stage": "write", "account": account, "web": True, "prompt": config.prompt(
            "write", account=account, handle=acc.get("handle", ""), persona=acc["persona"], n=n,
            now_vn=config.now().astimezone(config.VN).strftime("%A %d %B %Y, %H:%M"),
            signals=trends.render(trends.collect(account)), recent=_recent(all_posts, account),
            performance=_performance(all_posts, account))}
    return None


def next_ticket() -> dict:
    pending = sorted(jobs_dir().glob("*.job.json"))
    if pending:  # finish an open job before handing out a new one
        return json.loads(pending[0].read_text(encoding="utf-8"))["ticket"]
    job = plan()
    if job is None:
        return {"done": True, "reason": "queues full and no drafts to review"}
    job_id = f"{config.now().strftime('%Y%m%dT%H%M%S')}-{job['stage']}-{job['account']}"
    d = jobs_dir()
    (d / "system.md").write_text(config.prompt("system"), encoding="utf-8")
    prompt_file = d / f"{job_id}.prompt.md"
    prompt_file.write_text(job["prompt"], encoding="utf-8")
    ticket = {
        "done": False, "job_id": job_id, "stage": job["stage"], "account": job["account"], "web": job["web"],
        "system_file": str(d / "system.md"), "prompt_file": str(prompt_file),
        "output_file": str(d / f"{job_id}.out.json"),
        "instructions": ("Adopt system_file as your instructions and complete prompt_file. "
                         "Use web search/fetch to research and verify. "
                         f"Write ONLY a valid JSON object to output_file. Then run: meta agent submit {job_id}"),
    }
    (d / f"{job_id}.job.json").write_text(json.dumps({"ticket": ticket}, indent=2), encoding="utf-8")
    return ticket


def submit(job_id: str) -> str:
    d = jobs_dir()
    jf = d / f"{job_id}.job.json"
    if not jf.exists():
        raise SystemExit(f"no open job {job_id}")
    t = json.loads(jf.read_text(encoding="utf-8"))["ticket"]
    out = Path(t["output_file"])
    if not out.exists():
        raise SystemExit(f"output file missing: {out}")
    data = posts.parse_json(out.read_text(encoding="utf-8"))  # raises on bad output; job stays open
    if t["stage"] == "write":
        result = f"{len(posts.add_drafts(t['account'], data))} draft(s) added"
    else:
        result = ", ".join(f"{v} {k}" for k, v in posts.apply_reviews(data).items()) or "nothing changed"
    done = d / "done"
    done.mkdir(exist_ok=True)
    for f in d.glob(f"{job_id}.*"):
        f.replace(done / f.name)
    return f"{t['stage']} {t['account']}: {result}"


def abandon(job_id: str) -> None:
    for f in jobs_dir().glob(f"{job_id}.*"):
        f.unlink()
