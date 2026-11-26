"""`meta` command line."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import timedelta

from dotenv import load_dotenv

from . import agent, card, config, media, posts, threads, trends


def cmd_agent(a):
    if a.action == "next":
        print(json.dumps(agent.next_ticket(), ensure_ascii=False, indent=2))
    elif not a.job_id:
        sys.exit("job_id required")
    elif a.action == "submit":
        print(agent.submit(a.job_id))
    else:
        agent.abandon(a.job_id)
        print(f"abandoned {a.job_id}")


def cmd_queue(a):
    for p in posts.load():
        if p["state"] in ("pending", "approved", "draft"):
            score = p.get("review", {}).get("score", "-")
            print(f"\n[{p['state']}] {p['id']}  ({p['account']}, score {score}, {p['category']})\n"
                  f"{p['text']}\n  ↳ reply: {p['reply'] or '-'}\n  sources: {' '.join(p['sources'])}")


def _set_state(ids, frm, to):
    all_posts = posts.load()
    targets = [p for p in all_posts if p["state"] == frm] if ids == ["all"] else [posts.find(all_posts, i) for i in ids]
    for p in targets:
        if p["state"] != frm:
            sys.exit(f"{p['id']} is {p['state']}, not {frm}")
        p["state"] = to
    posts.save(all_posts)
    print(f"{len(targets)} post(s) -> {to}")


def cmd_approve(a):
    _set_state(a.ids, "pending", "approved")


def cmd_reject(a):
    all_posts = posts.load()
    for i in a.ids:
        posts.find(all_posts, i)["state"] = "rejected"
    posts.save(all_posts)
    print(f"{len(a.ids)} post(s) -> rejected")


def cmd_publish(a):
    all_posts = posts.load()
    posts.expire_stale(all_posts)
    at = config.now()
    for account in config.active_accounts():
        p = posts.due(all_posts, account, at, ignore_gap=a.now)
        if not p:
            print(f"{account}: nothing due (window, gap or empty queue)")
            continue
        if a.dry_run:
            print(f"{account}: would publish {p['id']}" + (f" with card: {p['card']!r}" if p.get("card") else "")
                  + f"\n{p['text']}")
            continue
        try:  # one account failing (no token, API error) must not stop the others
            image_url = None
            if p.get("card"):
                handle = config.settings()["accounts"][account].get("handle", "")
                png = card.render(p["card"], handle, media.repo() / account / f"{p['id']}.png", seed=p["id"])
                image_url = p["image_url"] = media.host(png)
            # news without a card: show the article's preview so scrollers see who/what it is about
            link = p["sources"][0] if p.get("kind") == "news" and not image_url and p.get("sources") else None
            p["media_id"] = threads.publish_text(account, p["text"], image_url=image_url, link=link)
        except SystemExit as e:
            print(f"{account}: publish failed: {e}", file=sys.stderr)
            continue
        p["state"], p["published_at"] = "published", posts.iso(at)
        posts.save(all_posts)  # saved before the reply so a reply failure never re-posts the main text
        if p["reply"]:
            try:
                p["reply_id"] = threads.publish_text(account, p["reply"], reply_to=p["media_id"])
            except SystemExit as e:
                print(f"{account}: reply failed: {e}", file=sys.stderr)
        try:
            p["permalink"] = threads.permalink(account, p["media_id"])
        except SystemExit:
            p["permalink"] = ""
        print(f"{account}: published {p['id']} {p['permalink']}")
    posts.save(all_posts)


def cmd_delete(a):
    """Delete published posts (and their source reply) from Threads; keeps the record as state 'deleted'."""
    all_posts = posts.load()
    for pid in a.ids:
        p = posts.find(all_posts, pid)
        if p["state"] != "published":
            sys.exit(f"{pid} is {p['state']}, not published")
        if p.get("reply_id"):
            threads.delete(p["account"], p["reply_id"])
        threads.delete(p["account"], p["media_id"])
        p["state"], p["deleted_at"] = "deleted", posts.iso(config.now())
        posts.save(all_posts)
        print(f"deleted {pid} {p.get('permalink', '')}")


def cmd_track(a):
    all_posts = posts.load()
    cutoff = config.now() - timedelta(days=config.settings()["track"]["days"])
    n = 0
    for p in all_posts:
        if p["state"] == "published" and posts._ts(p, "published_at") > cutoff:
            p["insights"] = threads.insights(p["account"], p["media_id"])
            p["insights_at"] = posts.iso(config.now())
            n += 1
    posts.save(all_posts)
    print(f"insights updated for {n} post(s)")


def cmd_status(a):
    all_posts = posts.load()
    for account in config.settings()["accounts"]:
        mine = [p for p in all_posts if p["account"] == account]
        counts = {s: sum(1 for p in mine if p["state"] == s) for s in posts.STATES}
        print(f"{account}: " + (", ".join(f"{k} {v}" for k, v in counts.items() if v) or "empty"))


def cmd_trends(a):
    print(trends.render(trends.collect(a.slot)))


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")  # Vietnamese text on a cp1252 Windows console
    load_dotenv(config.root() / ".env")
    p = argparse.ArgumentParser(prog="meta", description="Threads content engine")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("auth", threads.auth), ("whoami", threads.whoami), ("refresh", threads.refresh)):
        s = sub.add_parser(name, help=f"Threads token: {name}")
        s.add_argument("slot", type=str.upper, choices=["A", "B"])
        s.set_defaults(fn=lambda a, fn=fn: fn(a.slot))
    ag = sub.add_parser("agent", help="job protocol for a Claude Code session acting as the model")
    ag.add_argument("action", choices=["next", "submit", "abandon"])
    ag.add_argument("job_id", nargs="?")
    ag.set_defaults(fn=cmd_agent)
    sub.add_parser("queue", help="show drafts, pending and approved posts").set_defaults(fn=cmd_queue)
    ap = sub.add_parser("approve", help="approve pending posts (ids or 'all')")
    ap.add_argument("ids", nargs="+")
    ap.set_defaults(fn=cmd_approve)
    rj = sub.add_parser("reject", help="reject posts by id")
    rj.add_argument("ids", nargs="+")
    rj.set_defaults(fn=cmd_reject)
    pb = sub.add_parser("publish", help="publish at most one due post per active account")
    pb.add_argument("--dry-run", action="store_true")
    pb.add_argument("--now", action="store_true", help="skip the min-gap check (window still applies)")
    pb.set_defaults(fn=cmd_publish)
    dl = sub.add_parser("delete", help="permanently delete published posts (and their reply) from Threads")
    dl.add_argument("ids", nargs="+")
    dl.set_defaults(fn=cmd_delete)
    sub.add_parser("track", help="pull insights for recent posts").set_defaults(fn=cmd_track)
    sub.add_parser("status", help="post counts by state").set_defaults(fn=cmd_status)
    tr = sub.add_parser("trends", help="print today's trend signals for an account")
    tr.add_argument("slot", type=str.upper, choices=["A", "B"], nargs="?", default="A")
    tr.set_defaults(fn=cmd_trends)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
