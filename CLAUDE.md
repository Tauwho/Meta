# Medium engine: notes for AI agents working in this repo

- Read `docs/POLICY.md` before changing anything that touches what gets published. The human gate is the reason stories stay paywall-eligible; do not add code that fills `[[HUMAN]]` slots, lowers `gate.min_edit_ratio` to bypass it, or automates logins/posting/engagement on Medium.
- Only public RSS feeds may be fetched from Medium automatically.
- Story state lives in `stories/<id>/state.json`; stages are in `store.AI_STAGES`. Work is modelled as jobs in `stages.py` (`story_job`, `apply_story`, `next_job`); both backends share them.
- Scheduled runs follow `docs/AGENT_RUN.md` (agent backend, no API key). API-backend Claude calls go through `llm.run` only (streaming, adaptive thinking, per-stage effort, refusal fallbacks, pause_turn handling).
- Run `pytest` after changes. Tests never call the API.
- Commits: no AI co-author trailers.
