# Medium engine

AI-centered pipeline for earning through the Medium Partner Program. Claude does the research, briefing, drafting scaffold, fact-checking, editing, packaging, scheduling and analytics. You do one step per story: add your own experience, make it yours, publish.

Why not fully autonomous: since May 2024 Medium bars AI-generated writing from the paywall, excludes it from distribution and Boost, and can revoke Partner Program enrollment. Medium's API has also been unsupported since 2023. Details in [docs/RESEARCH.md](docs/RESEARCH.md); the rules the pipeline enforces are in [docs/POLICY.md](docs/POLICY.md).

```
scout -> idea -> brief -> draft -> factcheck -> edit -> package -> GATE (you) -> published -> track
```

## Quick start

```bash
pip install -e .[dev]
cp .env.example .env          # add ANTHROPIC_API_KEY (or use `ant auth login`)
# fill config/voice.md and config/pipeline.yaml (niches, medium_handle)
pytest
medium scout                  # research + rank ideas  -> data/ideas.jsonl
medium new                    # make a story from the best idea
medium run <id>               # AI stages up to the gate -> stories/<id>/GATE.md
# ... do the gate (see GATE.md), publish on Medium ...
medium gate done <id> --url https://medium.com/@you/...
medium track                  # confirm via RSS, ingest data/earnings/*.csv
medium status
```

`medium run --all` keeps up to `cadence.max_waiting_at_gate` stories ready for you. The GitHub Actions workflow runs scout weekly and run/track daily (needs the `ANTHROPIC_API_KEY` secret).

## Layout

| Path | What |
|---|---|
| `config/pipeline.yaml` | niches, model + effort per stage, word counts, gate thresholds, cadence, scout weights |
| `config/voice.md` | your voice and experience; every stage reads it |
| `prompts/` | one prompt per stage (`$placeholders`) |
| `src/medium_engine/` | `cli`, `stages`, `gate`, `track`, `llm`, `rss`, `store`, `config` |
| `stories/<id>/` | `state.json`, `brief.md`, `draft.md`, `factcheck.md`, `edited.md`, `package/`, `GATE.md` |
| `data/` | `ideas.jsonl`, `performance.json`, `earnings/` (your stats exports, gitignored) |
| `docs/` | research, pipeline, policy, roadmap |
