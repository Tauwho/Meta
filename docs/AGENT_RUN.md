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
3. `meta publish` (posts at most one due post per account; does nothing within the gap or with an empty approved queue). If anything in this run printed an error, work through **Self-healing** below before step 4.
4. `meta status`.
5. Commit and push: `git add data/posts.jsonl`, `git commit -m "agent run <date>: <what happened>"`, `git push`. No AI co-author trailer.
6. Final message: jobs done, posts published (permalink), posts now waiting for approval (count), anything abandoned or failing, and every self-healing fix you made (what failed, what you did, whether it worked).

## Self-healing

Fix what you can inside this run, then report it. Work down this table; at most 2 attempts per problem, then stop and report.

**Golden rule before any publish retry:** run `meta recent <A|B>` and check the post is not already live (same text in the last few posts). If it is live, never publish it again: report it instead (the user decides how to record it).

| Error (from `meta publish`, `track`, `agent`, git) | Fix |
|---|---|
| `Invalid parameter` on publish of a post with a `poll`, `topic_tag`, `quote_post_id` or `card` | `meta clear <post id> <that field>` (start with `poll`, then `quote_post_id`, then `topic_tag`, then `card`), then `meta publish --now`. One field per attempt. |
| `requested resource does not exist`, `timed out`, `Please retry`, HTTP 5xx, `temporarily unavailable` | Transient on Meta's side. `meta recent <slot>` (golden rule), wait 60s, `meta publish --now` once. |
| Rate limit (`limit`, `too many calls`, code 4/17/32/613) | Do not retry; the next hourly run publishes it. Report. |
| Token error (`Error validating access token`, `Session has expired`, `OAuthException` code 190) | `meta refresh <slot>`, then retry the failed step once. If refresh fails too, report "user must run `meta auth <slot>`" and continue with the other account. |
| Permission error (`does not have permission`, code 10/200) on an optional feature | `meta clear` that feature from the post and publish; report which permission is missing. |
| Card hosting fails (git error in `media/`, image URL never serves) | `git -C media pull --rebase --autostash` and retry once; still failing: `meta clear <post id> card` and publish as text. |
| `git push` rejected | `git pull --rebase --autostash`, then push again. Merge conflict in `data/posts.jsonl`: keep both sides' records (union by `id`; for the same id keep the one with the later state, published > approved), never drop a published record. |
| `meta agent submit` keeps failing validation | Covered in step 2.5. |
| Python traceback from the `meta` CLI itself (a code bug, not an API error) | You may fix the bug: smallest change in `src/meta_engine/` only, add or update a test in `tests/`, `.venv\Scripts\python -m pytest -q` must pass, then commit it **separately** (`fix: <what>`, no AI trailer) and rerun the failed step. If you cannot make tests pass, `git checkout -- src tests` and report. |

Never, even to fix an error: delete or edit published posts, change `config/`, `prompts/` or `docs/POLICY.md`, flip `require_approval`, touch `.env` other than through `meta refresh`, or bypass validation by editing `data/posts.jsonl` by hand (use `meta clear`).

## Rules

- Post text is Vietnamese publication copy for real readers. Any terse chat style you use with the user does not apply to it; follow `system_file` exactly.
- Never edit `config/`, `prompts/` or `.env` during a run, nor code except a bug fix under Self-healing, never approve posts yourself (`meta approve` is the user's), and never post, reply, like or follow on Threads outside `meta publish`.
