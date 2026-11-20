# Pipeline

One story moves through a fixed state machine. Every AI stage is idempotent and writes its output into `stories/<id>/`; `state.json` records where the story is.

```
 scout ──► idea ──► brief ──► draft ──► factcheck ──► edit ──► package ──► GATE (human) ──► published ──► track
  AI        AI       AI        AI          AI           AI        AI          you              RSS          AI
```

| Stage | Command | Reads | Writes | Notes |
|---|---|---|---|---|
| scout | `medium scout` | `config/pipeline.yaml` niches + tag RSS feeds + `data/performance.json` | `data/ideas.jsonl` | Claude + web search ranks ideas by fit, demand, competition, past performance |
| pick | `medium new [--idea N]` | `data/ideas.jsonl` | `stories/<id>/state.json` | Creates the story folder from the best unused idea |
| brief | `medium run <id>` | idea, `config/voice.md` | `brief.md` | Angle, reader, outline, title options, tags, target publication, `[[HUMAN]]` slots planned |
| draft | (same) | brief | `draft.md` | Scaffolding draft with `[[HUMAN: ...]]` placeholders where experience must go |
| factcheck | (same) | draft | `factcheck.md` | Claude + web search: every factual claim, verdict, source URL |
| edit | (same) | draft + factcheck | `edited.md` | Fixes wrong claims, tightens, readability; keeps placeholders |
| package | (same) | edited + brief | `package/story.md`, `package/meta.json`, `GATE.md` | Final title/subtitle, 5 tags, publication pitch, image prompt, checklist |
| gate | `medium gate done <id> --url URL` | `package/final.md` (your version) | `state.json` | Refuses if placeholders remain or edit ratio < threshold |
| track | `medium track` | author RSS + `data/earnings/*.csv` | `data/performance.json` | Confirms publish, ingests earnings, scores topics for scout |

`medium run <id>` advances a story through every AI stage until it reaches the gate. `medium run --all` does it for every story in progress. `medium status` lists stories by state.

## The gate in practice (~30–45 min per story)

1. Open `stories/<id>/GATE.md` and follow the checklist.
2. Copy `package/story.md` to `package/final.md`, rewrite it in your voice and fill every `[[HUMAN]]` slot.
3. Paste `final.md` into the Medium editor, add the cover image, tags, paywall on, submit to the publication in `meta.json` (or publish directly).
4. `medium gate done <id> --url https://medium.com/...`

## Automation

- `.github/workflows/pipeline.yml` runs `scout` weekly and `run --all` + `track` daily on GitHub Actions, then commits results. Needs the `ANTHROPIC_API_KEY` repository secret.
- Locally the same commands work from a shell or a scheduled task.
- Nothing in the pipeline touches Medium except public RSS reads.

## Cadence and queue

`config/pipeline.yaml` → `cadence.stories_per_week` caps how many stories `run --all` will prepare ahead of the gate (`cadence.max_waiting_at_gate`), so a backlog doesn't pile up.
