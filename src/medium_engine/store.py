"""Story state on disk: stories/<id>/state.json plus one file per stage."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import config

# Ordered AI stages, then the human gate, then post-publish.
AI_STAGES = ["brief", "draft", "factcheck", "edit", "package"]
STATES = ["idea", *AI_STAGES, "awaiting_human", "published"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slugify(text: str, limit: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:limit].rstrip("-") or "story"


@dataclass
class Story:
    id: str
    idea: dict
    state: str = "idea"
    history: list[dict] = field(default_factory=list)
    url: str | None = None

    @property
    def dir(self) -> Path:
        return config.stories_dir() / self.id

    def path(self, name: str) -> Path:
        return self.dir / name

    def read(self, name: str) -> str:
        return self.path(name).read_text(encoding="utf-8")

    def write(self, name: str, text: str) -> None:
        p = self.path(name)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def advance(self, new_state: str, note: str = "") -> None:
        if new_state not in STATES:
            raise ValueError(f"unknown state {new_state}")
        self.state = new_state
        self.history.append({"state": new_state, "at": _now(), "note": note})
        self.save()

    def next_stage(self) -> str | None:
        """The AI stage to run next, or None if the story is at/after the gate."""
        if self.state == "idea":
            return AI_STAGES[0]
        if self.state in AI_STAGES:
            i = AI_STAGES.index(self.state)
            return AI_STAGES[i + 1] if i + 1 < len(AI_STAGES) else None
        return None

    def save(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path("state.json").write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")


def create(idea: dict) -> Story:
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    base = f"{date}-{slugify(idea.get('title', 'story'))}"
    sid, n = base, 2
    while (config.stories_dir() / sid).exists():
        sid, n = f"{base}-{n}", n + 1
    story = Story(id=sid, idea=idea)
    story.history.append({"state": "idea", "at": _now(), "note": "created"})
    story.save()
    return story


def load(story_id: str) -> Story:
    data = json.loads((config.stories_dir() / story_id / "state.json").read_text(encoding="utf-8"))
    return Story(**data)


def all_stories() -> list[Story]:
    d = config.stories_dir()
    if not d.exists():
        return []
    return [load(p.parent.name) for p in sorted(d.glob("*/state.json"))]
