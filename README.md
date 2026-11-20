# Medium engine

AI-centered pipeline for earning through the Medium Partner Program. Claude does the research, briefing, drafting scaffold, fact-checking, editing, packaging, scheduling and analytics. You do one step per story: add your own experience, make it yours, publish.

Why not fully autonomous: since May 2024 Medium bars AI-generated writing from the paywall, excludes it from distribution and Boost, and can revoke Partner Program enrollment. Medium's API has also been unsupported since 2023. Details in [docs/RESEARCH.md](docs/RESEARCH.md); the rules the pipeline enforces are in [docs/POLICY.md](docs/POLICY.md).

```
scout -> idea -> brief -> draft -> factcheck -> edit -> review (auto-revise) -> package -> GATE (you) -> published -> track -> learn
```

Consistency comes from four layers: your voice (`config/voice.md`), the house style (`config/style.md`) enforced by a linter and a rubric review, exemplars + learned rules taken from your own published rewrites, and one cover template (`config/visual.md`). See [docs/QUALITY.md](docs/QUALITY.md).

## Quick start

```bash
pip install -e .[dev]
# fill config/voice.md and config/pipeline.yaml (niches, medium_handle)
pytest
# AI work runs on your Claude subscription: a scheduled Claude Code task follows
# docs/AGENT_RUN.md, looping `medium agent next` -> write output -> `medium agent submit`.
# Stories land at the gate: stories/<id>/GATE.md
# ... do the gate (see GATE.md), publish on Medium ...
medium gate done <id> --url https://medium.com/@you/...
medium track                  # confirm via RSS, ingest data/earnings/*.csv
medium learn                  # turn your rewrites into style rules
medium lint <id>              # style check; export <id> -> paste-ready HTML; cover <id> -> cover.png
medium status
```

The scheduled task (Claude desktop app, daily) keeps up to `cadence.max_waiting_at_gate` stories ready for you; it runs while the app is open, or on next launch. Optional: `llm.backend: api` + an API key enables `medium scout/run/learn` and the manual GitHub Actions workflow.

## Layout

| Path | What |
|---|---|
| `config/pipeline.yaml` | niches, model + effort per stage, word counts, gate thresholds, cadence, scout weights |
| `config/voice.md` | your voice and experience; every stage reads it |
| `config/style.md`, `config/visual.md` | house writing style and visual identity |
| `config/style-learned.md`, `config/exemplars/` | generated from your published rewrites |
| `prompts/` | one prompt per stage (`$placeholders`) |
| `src/medium_engine/` | `cli`, `stages`, `gate`, `track`, `llm`, `rss`, `store`, `config` |
| `stories/<id>/` | `state.json`, `brief.md`, `draft.md`, `factcheck.md`, `edited.md`, `package/`, `GATE.md` |
| `data/` | `ideas.jsonl`, `performance.json`, `earnings/` (your stats exports, gitignored) |
| `docs/` | research, pipeline, policy, roadmap |
