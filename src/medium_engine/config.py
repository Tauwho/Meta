"""Paths, config loading and prompt rendering."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from string import Template
from typing import Any

import yaml


def root() -> Path:
    """Project root: $MEDIUM_ROOT, else the nearest parent holding config/pipeline.yaml."""
    env = os.environ.get("MEDIUM_ROOT")
    if env:
        return Path(env).resolve()
    here = Path.cwd().resolve()
    for p in (here, *here.parents):
        if (p / "config" / "pipeline.yaml").exists():
            return p
    raise FileNotFoundError("config/pipeline.yaml not found; run inside the repo or set MEDIUM_ROOT")


def stories_dir() -> Path:
    return root() / "stories"


def data_dir() -> Path:
    return root() / "data"


@lru_cache(maxsize=1)
def settings() -> dict[str, Any]:
    with open(root() / "config" / "pipeline.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _read(rel: str, default: str = "") -> str:
    path = root() / rel
    return path.read_text(encoding="utf-8") if path.exists() else default


def voice() -> str:
    return _read("config/voice.md")


def style() -> str:
    return _read("config/style.md")


def learned() -> str:
    return _read("config/style-learned.md", "(none yet)")


def exemplars_dir() -> Path:
    return root() / "config" / "exemplars"


def exemplars(n: int | None = None) -> str:
    """The n most recent human-final stories, newest first."""
    if n is None:
        n = settings().get("quality", {}).get("exemplars_in_prompt", 2)
    files = sorted(exemplars_dir().glob("*.md"), reverse=True)[:n] if n else []
    if not files:
        return "(none yet; rely on the voice sample)"
    return "\n\n".join(f'<exemplar name="{f.stem}">\n{f.read_text(encoding="utf-8")}\n</exemplar>' for f in files)


def system_prompt() -> str:
    """Stable per run (no timestamps), so it caches well across stage calls."""
    return prompt("system", voice=voice(), style=style(), learned=learned(), exemplars=exemplars())


def prompt(name: str, **values: Any) -> str:
    """Render prompts/<name>.md with $placeholders (safe_substitute leaves JSON braces alone)."""
    text = (root() / "prompts" / f"{name}.md").read_text(encoding="utf-8")
    return Template(text).safe_substitute({k: str(v) for k, v in values.items()})
