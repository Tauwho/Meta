# Agent run (scheduled Claude Code task on a Claude subscription)

No API key. The scheduled Claude Code session *is* the model; the `medium` CLI decides what to do next and validates every output.

## Procedure

Work in `C:\Data\Singapore\SMU\Medium`. CLI: `.venv\Scripts\medium.exe` (if missing: `python -m venv .venv` then `.venv\Scripts\python -m pip install -e .`).

1. `git pull --ff-only`, then `medium track` (ignore network warnings).
2. Loop, at most **12 jobs** per run:
   1. `medium agent next` → JSON ticket. If `"done": true`, stop the loop.
   2. Read `system_file` and adopt it as your instructions for this job (author voice, house style, learned notes, exemplars). Read `prompt_file`: that is the task.
   3. If `web` is true, research and verify with WebSearch/WebFetch. If false, do not browse.
   4. Write **only** the deliverable to `output_file` with the Write tool: valid JSON when `fmt` is `json`, Markdown when `markdown`. No preamble, no commentary, no code fences around the whole thing.
   5. `medium agent submit <job_id>`. If it fails, read the error, fix `output_file`, submit again (max 2 retries). If still failing: `medium agent abandon <job_id>`, note it, continue.
3. `medium status`.
4. Commit and push: `git add stories data/ideas.jsonl data/performance.json config/style-learned.md` then `git commit -m "agent run <date>: <jobs done>"` and `git push`. No AI co-author trailer.
5. Final message: jobs done, stories now waiting at the gate (id + title), anything abandoned.

## Rules for the writing itself

- Output files are publication prose for a human reader. Any terse/compressed chat style you use with the user does **not** apply to them; follow `system_file` exactly.
- Never fill `[[HUMAN: ...]]` slots and never invent anecdotes, quotes, numbers or credentials. Those are the writer's job at the gate (see `docs/POLICY.md`).
- Do not touch Medium itself (no login, posting, clapping, following). Public pages via web search are fine.
- Do not edit `config/voice.md`, `config/style.md`, `config/pipeline.yaml` or code during a run.
