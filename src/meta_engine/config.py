"""Paths, settings and prompt rendering."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from string import Template
from typing import Any

import yaml

VN = timezone(timedelta(hours=7))  # fixed offset: Vietnam has no DST, and Windows lacks tzdata


def root() -> Path:
    """Project root: $META_ROOT, else the nearest parent holding config/meta.yaml."""
    env = os.environ.get("META_ROOT")
    if env:
        return Path(env).resolve()
    here = Path.cwd().resolve()
    for p in (here, *here.parents):
        if (p / "config" / "meta.yaml").exists():
            return p
    raise FileNotFoundError("config/meta.yaml not found; run inside the repo or set META_ROOT")


def data_dir() -> Path:
    d = root() / "data"
    d.mkdir(exist_ok=True)
    return d


@lru_cache(maxsize=1)
def settings() -> dict[str, Any]:
    with open(root() / "config" / "meta.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def active_accounts() -> dict[str, dict]:
    return {k: v for k, v in settings()["accounts"].items() if v.get("active")}


def now() -> datetime:
    return datetime.now(timezone.utc)


def prompt(name: str, **values: Any) -> str:
    """Render prompts/<name>.md with $placeholders (safe_substitute leaves JSON braces alone)."""
    text = (root() / "prompts" / f"{name}.md").read_text(encoding="utf-8")
    return Template(text).safe_substitute({k: str(v) for k, v in values.items()})
