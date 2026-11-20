"""Thin wrapper over the Anthropic Messages API used by every AI stage."""

from __future__ import annotations

import json
import re
from typing import Any

import anthropic

from . import config


class LLMError(RuntimeError):
    pass


def _client() -> anthropic.Anthropic:
    # Credentials resolve from ANTHROPIC_API_KEY or an `ant auth login` profile.
    return anthropic.Anthropic()


def run(prompt: str, *, stage: str, web: bool = False, max_tokens: int = 64000) -> str:
    """Send one prompt (plus the shared system prompt) and return the final text.

    Streams to avoid HTTP timeouts on long outputs, uses adaptive thinking with a
    per-stage effort level, enables server-side refusal fallbacks, and resumes
    `pause_turn` stops that long web-search turns can produce.
    """
    s = config.settings()["llm"]
    # voice + style + learned notes + exemplars are identical across every stage call,
    # so cache the system block (cuts input cost on stages 2..n of a run).
    system = [{"type": "text", "text": config.system_prompt(), "cache_control": {"type": "ephemeral"}}]
    tools: list[dict[str, Any]] = []
    if web:
        tools.append({
            "type": "web_search_20260209",
            "name": "web_search",
            "max_uses": s.get("web_search_max_uses", 8),
        })

    messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
    client = _client()
    for _ in range(6):
        kwargs: dict[str, Any] = dict(
            model=s["model"],
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            thinking={"type": "adaptive"},
            output_config={"effort": s.get("effort", {}).get(stage, "high")},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if tools:
            kwargs["tools"] = tools
        with client.beta.messages.stream(**kwargs) as stream:
            msg = stream.get_final_message()

        if msg.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": msg.content})
            continue
        if msg.stop_reason == "refusal":
            raise LLMError(f"{stage}: model declined ({getattr(msg, 'stop_details', None)})")
        if msg.stop_reason == "max_tokens":
            raise LLMError(f"{stage}: output hit max_tokens={max_tokens}")
        return "".join(b.text for b in msg.content if b.type == "text").strip()
    raise LLMError(f"{stage}: too many pause_turn continuations")


def extract_json(text: str) -> Any:
    """Parse the first JSON object in a model reply (tolerates ```json fences)."""
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    candidate = fenced.group(1) if fenced else text[text.find("{"): text.rfind("}") + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise LLMError(f"could not parse JSON from model reply: {e}") from e
