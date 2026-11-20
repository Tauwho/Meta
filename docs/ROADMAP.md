# Plan

## Phase 0 — Setup (week 1)

- [ ] Check Singapore is on Medium's Partner Program supported-countries list; set up Stripe payouts
- [ ] Become a Medium member and join the Partner Program
- [ ] Fill `config/voice.md` (who you are, experience you can draw on, tone, words you never use)
- [ ] Set niches + seed tags + Medium handle in `config/pipeline.yaml`
- [ ] Put `ANTHROPIC_API_KEY` in `.env` (local) and as a GitHub repo secret (Actions)
- [ ] `pip install -e .[dev]` and `pytest`

## Phase 1 — First 10 stories (weeks 2–5)

- [ ] `medium scout`, then `medium new` + `medium run` for 3 stories at a time
- [ ] Gate each story, publish 2–3/week
- [ ] Submit each to a publication; track acceptance in `meta.json`
- KPI: 10 published, ≥3 accepted by publications, ≥1 Boost

## Phase 2 — Feedback loop (weeks 6–12)

- [ ] Drop earnings/stats exports into `data/earnings/` weekly; `medium track`
- [ ] Tune `scout` weights from `data/performance.json`
- [ ] Turn on the GitHub Actions schedule
- KPI: member reading time trend up week over week; first payout

## Phase 3 — Scale what works

- [ ] Double down on the top topic cluster; series and lists
- [ ] Consider own publication on Medium for the niche
- [ ] Optional: newsletter capture, disclosed affiliate links

## Cost estimate (Claude API)

Roughly 6 model calls per story (brief, draft, factcheck with search, edit, package, plus scout amortised) on `claude-opus-5-5` at $4/$20 per MTok: about $0.30–$1.00 per story depending on length and search use. Switch `llm.model` to `claude-sonnet-5-5` in config to cut that roughly in half.
