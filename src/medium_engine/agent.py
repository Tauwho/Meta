"""Agent backend: a Claude Code session (e.g. a scheduled task on a Claude subscription) is the model.

Protocol, one job at a time:
  medium agent next          -> prints a JSON job ticket and writes jobs/<id>.prompt.md + jobs/system.md
  (session writes its answer to the ticket's output_file)
  medium agent submit <id>   -> validates + applies the output, advances the pipeline
Repeat until `next` prints {"done": true}.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from . import config, stages


def jobs_dir() -> Path:
    d = config.root() / "jobs"
    d.mkdir(exist_ok=True)
    return d


def next_ticket() -> dict:
    pending = sorted(jobs_dir().glob("*.job.json"))
    if pending:  # finish an open job before handing out a new one
        return json.loads(pending[0].read_text(encoding="utf-8"))["ticket"]
    job = stages.next_job()
    if job is None:
        return {"done": True, "reason": "nothing to do: queue at the gate is full or all stories are waiting for you"}

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    job_id = f"{ts}-{job.stage}"
    d = jobs_dir()
    (d / "system.md").write_text(config.system_prompt(), encoding="utf-8")
    prompt_file = d / f"{job_id}.prompt.md"
    prompt_file.write_text(job.prompt, encoding="utf-8")
    out_file = d / f"{job_id}.out.{'json' if job.fmt == 'json' else 'md'}"
    ticket = {
        "done": False,
        "job_id": job_id,
        **job.describe(),
        "system_file": str(d / "system.md"),
        "prompt_file": str(prompt_file),
        "output_file": str(out_file),
        "instructions": (
            "Adopt system_file as your instructions and complete prompt_file. "
            + ("Use web search/fetch to research and verify. " if job.web else "Do not browse. ")
            + ("Write ONLY a valid JSON object to output_file. " if job.fmt == "json"
               else "Write ONLY the requested Markdown to output_file, no preamble. ")
            + f"Then run: medium agent submit {job_id}"
        ),
    }
    (d / f"{job_id}.job.json").write_text(json.dumps({"ticket": ticket, "job": asdict(job)}, indent=2),
                                          encoding="utf-8")
    return ticket


def submit(job_id: str) -> str:
    d = jobs_dir()
    jf = d / f"{job_id}.job.json"
    if not jf.exists():
        raise SystemExit(f"no open job {job_id}")
    data = json.loads(jf.read_text(encoding="utf-8"))
    job = stages.Job(**data["job"])
    out = Path(data["ticket"]["output_file"])
    if not out.exists():
        raise SystemExit(f"output file missing: {out}")
    stages.apply(job, out.read_text(encoding="utf-8"))  # raises on bad output; job stays open for a retry
    done = d / "done"
    done.mkdir(exist_ok=True)
    for f in d.glob(f"{job_id}.*"):
        f.replace(done / f.name)
    return f"applied {job.stage}" + (f" to {job.story_id}" if job.story_id else "")


def abandon(job_id: str) -> None:
    for f in jobs_dir().glob(f"{job_id}.*"):
        f.unlink()
