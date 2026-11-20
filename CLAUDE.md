# Medium engine: notes for AI agents working in this repo

- Read `docs/POLICY.md` before changing anything that touches what gets published. The human gate is the reason stories stay paywall-eligible; do not add code that fills `[[HUMAN]]` slots, lowers `gate.min_edit_ratio` to bypass it, or automates logins/posting/engagement on Medium.
- Only public RSS feeds may be fetched from Medium automatically.
- Story state lives in `stories/<id>/state.json`; stages are in `store.AI_STAGES`. Add a stage by adding a prompt in `prompts/`, a branch in `stages.run_stage`, and the name to `AI_STAGES`.
- Claude calls go through `llm.run` only (streaming, adaptive thinking, per-stage effort, refusal fallbacks, pause_turn handling).
- Run `pytest` after changes. Tests never call the API.
- Commits: no AI co-author trailers.
