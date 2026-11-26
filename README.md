# Meta engine

Trend-driven Threads content for Vietnamese audiences. A scheduled Claude Code task (on a Claude subscription, no API key) reads what Vietnam is searching and reading today, researches it, writes short Vietnamese posts, reviews them, and publishes through the official Threads API.

```
trends (Google Trends VN + VN news RSS)
  -> write   (agent job: research + draft N posts, sources required)
  -> review  (agent job: fact-check + hard rules + score; pass / fix / reject)
  -> pending -> `meta approve` (only while publish.require_approval is true)
  -> approved -> `meta publish` (posting window, gap, expiry) -> post + source reply
  -> `meta track` (views, likes, replies, reposts, quotes, shares) -> fed back into the next write job
```

## Setup

```powershell
python -m venv .venv; .venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\meta auth A      # one-time per account; see docs/RESEARCH.md for the Meta app
.venv\Scripts\pytest
```

## Commands

| Command | What |
|---|---|
| `meta trends` | today's trend signals |
| `meta agent next / submit <id> / abandon <id>` | job protocol for the scheduled Claude session (`docs/AGENT_RUN.md`) |
| `meta queue` | drafts, pending and approved posts with their text and sources |
| `meta approve <id...>\|all`, `meta reject <id...>` | your gate |
| `meta publish [--dry-run]` | at most one due post per active account |
| `meta track` | pull insights for posts from the last 14 days |
| `meta status` | counts by state |
| `meta auth / whoami / refresh A\|B` | Threads tokens (refresh before 60 days) |

## Files

| Path | What |
|---|---|
| `config/meta.yaml` | accounts + personas, cadence, approval switch, review threshold, trend feeds |
| `prompts/` | `system.md` (voice + hard rules), `write.md`, `review.md` |
| `data/posts.jsonl` | every post with state, sources, review, Threads ids and insights |
| `docs/POLICY.md` | what the engine must never post, and why |
| `.env` | app id/secret and per-account tokens (gitignored) |
