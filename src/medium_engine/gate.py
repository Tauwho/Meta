"""The human gate: checklist, and the checks that must pass before a story counts as published."""

from __future__ import annotations

import difflib
import re

from . import config, store

PLACEHOLDER = re.compile(r"\[\[HUMAN:.*?\]\]", re.S)


def placeholders(text: str) -> list[str]:
    return PLACEHOLDER.findall(text)


def edit_ratio(ai_text: str, final_text: str) -> float:
    """Fraction of the text that changed between the AI package and the human's final (0..1)."""
    return round(1 - difflib.SequenceMatcher(None, ai_text, final_text, autojunk=False).ratio(), 4)


def write_gate_checklist(story: store.Story, meta: dict) -> None:
    slots = placeholders(story.read("edited.md"))
    pub = meta.get("publication", {})
    min_ratio = config.settings()["gate"]["min_edit_ratio"]
    lines = [
        f"# Gate: {meta.get('title', story.id)}",
        "",
        f"*{meta.get('subtitle', '')}*",
        "",
        "## Checklist",
        "",
        "- [ ] Copy `package/story.md` to `package/final.md`",
        f"- [ ] Fill all {len(slots)} `[[HUMAN]]` slots with your own experience (do not ask an AI to fill them)",
        f"- [ ] Rewrite in your voice (gate needs at least {int(min_ratio * 100)}% changed vs the AI package)",
        "- [ ] Check every non-OK row in `factcheck.md`; cut what you can't stand behind",
        f"- [ ] Paste into Medium; cover image via Unsplash: `{meta.get('cover_image', {}).get('unsplash_query', '')}`",
        f"- [ ] Tags: {', '.join(meta.get('tags', []))}",
        "- [ ] Paywall ON (Partner Program)",
        f"- [ ] Submit to **{pub.get('name', '?')}** ({pub.get('url', '')}) or publish directly",
        f"- [ ] `medium gate done {story.id} --url <story url>`",
        "",
        "## Slots to fill",
        "",
        *[f"{i}. {s}" for i, s in enumerate(slots, 1)],
        "",
        "## Publication pitch",
        "",
        pub.get("pitch", ""),
        "",
    ]
    story.write("GATE.md", "\n".join(lines))


def check(story: store.Story) -> list[str]:
    """Return a list of problems; empty means the gate passes."""
    g = config.settings()["gate"]
    final_path = story.path("package/final.md")
    if not final_path.exists():
        return ["package/final.md does not exist (copy story.md there and make it yours)"]
    final = final_path.read_text(encoding="utf-8")
    problems = []
    left = placeholders(final)
    if g.get("require_no_placeholders", True) and left:
        problems.append(f"{len(left)} [[HUMAN]] slot(s) still unfilled")
    ratio = edit_ratio(story.read("package/story.md"), final)
    if ratio < g["min_edit_ratio"]:
        problems.append(f"edit ratio {ratio:.0%} < required {g['min_edit_ratio']:.0%}: rewrite more in your own voice")
    return problems


def done(story: store.Story, url: str) -> None:
    if story.state != "awaiting_human":
        raise SystemExit(f"{story.id} is in state '{story.state}', not awaiting_human")
    if not url.startswith("https://"):
        raise SystemExit("url must be the published https:// story link")
    problems = check(story)
    if problems:
        raise SystemExit("gate refused:\n- " + "\n- ".join(problems))
    story.url = url
    story.advance("published", f"edit_ratio={edit_ratio(story.read('package/story.md'), story.read('package/final.md'))}")
