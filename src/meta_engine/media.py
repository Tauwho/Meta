"""Public image hosting: card PNGs go to the public Tauwho/meta-media repo (cloned at ./media),
because the Threads API only accepts images by public URL."""

from __future__ import annotations

import subprocess
import time
import urllib.request
from pathlib import Path

from . import config

RAW = "https://raw.githubusercontent.com/Tauwho/meta-media/main/"


def repo() -> Path:
    d = config.root() / "media"
    if not (d / ".git").exists():
        raise SystemExit("media/ is not a clone of Tauwho/meta-media; run: git clone https://github.com/Tauwho/meta-media.git media")
    return d


def _git(*args: str) -> None:
    subprocess.run(["git", "-C", str(repo()), *args], check=True, capture_output=True)


def host(png: Path) -> str:
    """Commit + push one PNG that already sits inside media/, return its public URL once it serves."""
    rel = png.relative_to(repo()).as_posix()
    _git("pull", "-q", "--ff-only")
    _git("add", rel)
    _git("commit", "-q", "-m", f"card {rel}")
    _git("push", "-q")
    url = RAW + rel
    for _ in range(12):  # raw.githubusercontent.com can lag a few seconds after a push
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=15) as r:
                if r.status == 200:
                    return url
        except Exception:
            pass
        time.sleep(5)
    raise SystemExit(f"image not reachable after push: {url}")
