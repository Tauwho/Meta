# Quality and consistency system

Goal: every story reads like the same writer, clears a fixed quality bar before it reaches you, and looks like part of one series in the feed.

## Audit (2026-11-20) — what was missing in v0.1

| Gap | Risk | Fix in v0.2 |
|---|---|---|
| Only `voice.md` steered style; no structural rules | Stories drift in shape, length, formatting | `config/style.md` house style (story shape, paragraphs, formatting, spelling, AI-tell list) |
| No measurable checks | AI tics and over-long paragraphs slip through; you catch them by hand | `lint.py` deterministic linter, errors block the gate |
| One-pass edit, no quality bar | Weak drafts reach the gate and cost you more rewrite time | `review` stage: 7-criterion rubric, auto-revise up to 2 rounds until average ≥ 4.0 and lint clean |
| Voice sample is ~80 words | Model can't lock onto rhythm | `config/exemplars/`: every published final becomes a style reference in the prompt |
| Your rewrites were thrown away | Same corrections every story | `medium learn`: diffs AI package vs your final, maintains `config/style-learned.md` (max 25 rules, highest priority in the prompt) |
| No visual identity | Random Unsplash covers, nothing recognisable | `config/visual.md` + `medium cover`: one typographic template, niche colour, fixed palette and fonts |
| Markdown pastes badly into Medium | Formatting lost, manual fixing | `medium export`: paste-ready HTML |
| Big system prompt resent each stage | Cost | System block cached (`cache_control`) |

## Open issues in `config/voice.md` (yours to fix)

1. **"Experience I can draw on" is abstract.** The draft stage plans `[[HUMAN]]` slots and scout scores "fit" from this list. Abstract entries ("learning by doing") give generic slots and generic ideas. List concrete things: projects, roles, courses, places, failures, numbers you can share.
2. **Niches and voice don't meet.** `pipeline.yaml` niches are internships, CS student life, payments engineering; `voice.md` mentions none of them. Either add matching experience or change the niches.
3. **Sample is short (~80 words).** Aim for 200–400 words of your own prose. Exemplars will take over once you publish a few stories.
4. Stray `-` at the end of the fourth experience bullet.

## How the layers fit

```
voice.md  ─┐
style.md  ─┼─► system prompt (cached) ─► brief / draft / edit / revise
learned   ─┤                                     │
exemplars ─┘                                     ▼
                                   lint (deterministic)  +  review (rubric)
                                                 │ below bar? revise (≤2x)
                                                 ▼
                                   package ─► cover.png + GATE.md quality report
                                                 ▼
                                   you: final.md ─► gate (lint errors block) ─► publish
                                                 ▼
                                   exemplar saved + `medium learn` updates style-learned.md
```

Priority when rules conflict: learned notes > voice > house style.

## Tuning

- Too many revisions or tokens: lower `quality.review.max_revisions` or `min_score`.
- Linter too strict for your taste: edit thresholds under `quality.lint`; move phrases in/out of `banned_phrases`.
- Different look: change `visual.palette`, `visual.niche_colors`, fonts; `medium cover <id>` regenerates.
- Sample cover: `docs/assets/cover-sample.png`.
