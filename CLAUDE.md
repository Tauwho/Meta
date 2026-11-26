# Meta engine: notes for AI agents working in this repo

- Threads content pipeline for Vietnamese audiences; see README.md. Scheduled runs follow `docs/AGENT_RUN.md`.
- Read `docs/POLICY.md` before changing anything that decides what gets published. Do not remove the review stage, the source requirement, or the hard rules in `prompts/system.md`; do not flip `publish.require_approval` unless the user asks.
- Only the official Threads API publishes. No browser automation of Threads/Instagram, no likes/follows/engagement automation, and the two accounts never interact with each other.
- Tokens and the app secret live only in `.env`; never print, log or commit them.
- Post state lives in `data/posts.jsonl` (`posts.py`); agent jobs are `write` and `review` (`agent.py`).
- Run `pytest` after changes. Tests never call the network.
- Commits: no AI co-author trailers.
