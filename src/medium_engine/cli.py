"""`medium` command line."""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

from . import config, gate, stages, store, track


def cmd_scout(a):
    new = stages.scout()
    print(f"{len(new)} new ideas; top of queue:")
    for i, idea in enumerate([x for x in stages.load_ideas() if x.get("status") == "new"][:10]):
        print(f"  [{i}] {idea.get('score', 0):.2f}  {idea['title']}")


def cmd_new(a):
    s = store.create(stages.pick_idea(a.idea))
    print(s.id)


def cmd_run(a):
    if a.all:
        stages.run_all()
        return
    if not a.id:
        sys.exit("give a story id or --all")
    s = stages.run_to_gate(store.load(a.id))
    print(f"{s.id}: {s.state}" + ("  -> open GATE.md" if s.state == "awaiting_human" else ""))


def cmd_status(a):
    for s in store.all_stories():
        print(f"{s.state:15} {s.id}" + (f"  {s.url}" if s.url else ""))


def cmd_gate(a):
    s = store.load(a.id)
    if a.action == "check":
        problems = gate.check(s)
        print("gate passes" if not problems else "\n".join(f"- {p}" for p in problems))
    else:
        if not a.url:
            sys.exit("--url is required for `gate done`")
        gate.done(s, a.url)
        print(f"{s.id}: published")


def cmd_track(a):
    missing = track.confirm_published()
    if missing:
        print("not seen in author RSS (may just be older than the feed):", *missing, sep="\n  ")
    perf = track.ingest_earnings()
    for niche, p in perf["by_niche"].items():
        print(f"  {niche}: {p['stories']} stories, ${p['earnings_usd']}, score {p['score']}")


def main(argv=None):
    load_dotenv(config.root() / ".env")
    p = argparse.ArgumentParser(prog="medium")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scout", help="research and rank new story ideas").set_defaults(fn=cmd_scout)
    n = sub.add_parser("new", help="create a story from the best unused idea")
    n.add_argument("--idea", type=int, help="index from `medium scout` output")
    n.set_defaults(fn=cmd_new)
    r = sub.add_parser("run", help="run AI stages up to the human gate")
    r.add_argument("id", nargs="?")
    r.add_argument("--all", action="store_true")
    r.set_defaults(fn=cmd_run)
    sub.add_parser("status", help="list stories by state").set_defaults(fn=cmd_status)
    g = sub.add_parser("gate", help="human gate: check or mark done")
    g.add_argument("action", choices=["check", "done"])
    g.add_argument("id")
    g.add_argument("--url")
    g.set_defaults(fn=cmd_gate)
    sub.add_parser("track", help="confirm publishes and ingest earnings").set_defaults(fn=cmd_track)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
