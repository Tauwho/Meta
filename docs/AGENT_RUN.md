# Agent run (scheduled Claude Code task)

No API key. The scheduled session *is* the model; the `meta` CLI decides what to do and validates every output.

## Procedure

Work in `C:\Data\Singapore\SMU\Meta`. CLI: `.venv\Scripts\meta.exe` (if missing: `python -m venv .venv` then `.venv\Scripts\python -m pip install -e .`).

1. `git pull --ff-only`, then `meta track` (if it fails with a token error, report it and continue).
2. Loop, at most **4 jobs** per run:
   1. `meta agent next` -> JSON ticket. If `"done": true`, stop the loop.
   2. Read `system_file` and adopt it as your instructions for this job. Read `prompt_file`: that is the task.
   3. Research with WebSearch/WebFetch. Open the sources you cite; never cite a page you did not read.
   4. Write **only** the JSON object to `output_file` with the Write tool. No preamble, no code fence.
   5. `meta agent submit <job_id>`. If it fails, read the error, fix `output_file`, submit again (max 2 retries). Still failing: `meta agent abandon <job_id>`, note it, continue.
3. `meta publish` (posts at most one due post per account; does nothing outside 07:00-23:00 Vietnam time, within the gap, or with an empty approved queue).
4. `meta status`.
5. Commit and push: `git add data/posts.jsonl`, `git commit -m "agent run <date>: <what happened>"`, `git push`. No AI co-author trailer.
6. Final message: jobs done, posts published (permalink), posts now waiting for approval (count), anything abandoned or failing.

## Rules

- Post text is Vietnamese publication copy for real readers. Any terse chat style you use with the user does not apply to it; follow `system_file` exactly.
- Never edit `config/`, `prompts/`, code or `.env` during a run, never approve posts yourself (`meta approve` is the user's), and never post, reply, like or follow on Threads outside `meta publish`.
