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


def voice() -> str:
    path = root() / "config" / "voice.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def prompt(name: str, **values: Any) -> str:
    """Render prompts/<name>.md with $placeholders (safe_substitute leaves JSON braces alone)."""
    text = (root() / "prompts" / f"{name}.md").read_text(encoding="utf-8")
    return Template(text).safe_substitute({k: str(v) for k, v in values.items()})
