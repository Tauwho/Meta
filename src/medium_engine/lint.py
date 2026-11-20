"""Deterministic style linter: the measurable half of config/style.md and config/voice.md.

Runs after edit (fed back into review/revise), at package (shown in GATE.md) and
at the gate on the human's final.md. Errors block the gate; warnings do not.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import config

US_SPELLINGS = {
    "color": "colour", "favorite": "favourite", "behavior": "behaviour", "honor": "honour",
    "center": "centre", "analyze": "analyse", "organize": "organise", "realize": "realise",
    "recognize": "recognise", "prioritize": "prioritise", "optimize": "optimise",
    "summarize": "summarise", "license": "licence (noun)", "program": "programme (non-software)",
    "catalog": "catalogue", "traveling": "travelling", "modeling": "modelling", "labeled": "labelled",
}
PLACEHOLDER = re.compile(r"\[\[HUMAN:.*?\]\]", re.S)
# First-person experience claims. In AI-written text these must live inside [[HUMAN]] slots.
FIRST_PERSON = re.compile(
    r"\b(in my (experience|view|internship|work)|i (learned|learnt|realised|realized|noticed|found|remember|"
    r"worked on|built|joined|spent|saw|used to)|my (internship|team|manager|job|first|own)|"
    r"we (built|shipped|had|used|learned|learnt))\b", re.I)


@dataclass
class Issue:
    level: str  # "error" | "warn"
    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level}] {self.rule}: {self.message}"


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def markdown(self) -> str:
        s = self.stats
        head = (f"words {s.get('words')}, ~{s.get('reading_minutes')} min, "
                f"avg sentence {s.get('sentence_avg')} words, sections {s.get('sections')}")
        if not self.issues:
            return f"{head}\n\nNo issues."
        return head + "\n\n" + "\n".join(f"- {i}" for i in self.issues)


def voice_banned() -> list[str]:
    """Quoted phrases from the '## Never' section of voice.md."""
    text = config.voice()
    m = re.search(r"^## Never\s*$(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return []
    out = []
    for q in re.findall(r"[“\"]([^”\"]+)[”\"]", m.group(1)):
        q = q.strip().strip(",.;:").strip().replace("’", "'")
        if q:
            out.append(q.lower())
    return out


def _parse(md: str) -> dict:
    lines = md.replace("\r\n", "\n").split("\n")
    title = subtitle = ""
    headings: list[tuple[int, str]] = []
    blocks: list[str] = []
    sections: list[list[str]] = [[]]
    list_runs: list[int] = []
    in_code, buf, run = False, [], 0

    def flush():
        nonlocal buf
        if buf:
            blocks.append(" ".join(buf).strip())
            sections[-1].append(blocks[-1])
            buf = []

    for line in lines:
        st = line.strip()
        if st.startswith("```"):
            in_code = not in_code
            flush()
            continue
        if in_code:
            continue
        hm = re.match(r"^(#{1,6})\s+(.*)$", st)
        if hm:
            flush()
            level = len(hm.group(1))
            if level == 1 and not title:
                title = hm.group(2).strip()
            else:
                headings.append((level, hm.group(2).strip()))
                sections.append([])
            continue
        if title and not subtitle and not blocks and re.fullmatch(r"[*_].+[*_]", st):
            subtitle = st.strip("*_ ").strip()
            continue
        if re.match(r"^([-*+]|\d+\.)\s+", st):
            flush()
            run += 1
            continue
        if run:
            list_runs.append(run)
            run = 0
        if not st or st.startswith(("!", ">")):
            flush()
            continue
        buf.append(st)
    flush()
    if run:
        list_runs.append(run)
    return {"title": title, "subtitle": subtitle, "headings": headings,
            "paragraphs": [b for b in blocks if b], "sections": sections, "list_runs": list_runs}


def _sentences(text: str) -> list[str]:
    text = PLACEHOLDER.sub("", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"“(])", text)
    return [p for p in parts if len(p.split()) >= 1]


def lint(md: str, ai: bool = False) -> Report:
    """ai=True for AI-written text (before the gate): adds checks for invented experience and slot count."""
    cfg = config.settings()["quality"]["lint"]
    p = _parse(md)
    rep = Report()
    add = lambda lvl, rule, msg: rep.issues.append(Issue(lvl, rule, msg))  # noqa: E731

    body = "\n".join(p["paragraphs"])
    plain = PLACEHOLDER.sub("", body)
    words = len(plain.split())
    sents = [s for para in p["paragraphs"] for s in _sentences(para)]
    lens = [len(s.split()) for s in sents] or [0]
    rep.stats = {
        "words": words,
        "reading_minutes": round(words / 238) or 1,
        "sentence_avg": round(sum(lens) / len(lens), 1),
        "sections": len([h for h in p["headings"] if h[0] == 2]),
        "placeholders": len(PLACEHOLDER.findall(md)),
    }

    # length vs target; each unfilled [[HUMAN]] slot is budgeted at slot_words
    lo_w, hi_w = config.settings()["story"]["target_words"]
    slot_words = cfg.get("slot_words", 150)
    projected = words + rep.stats["placeholders"] * slot_words
    if words > 200 and not lo_w <= projected <= hi_w:
        how = (f"{words} words + {rep.stats['placeholders']} slot(s) x ~{slot_words} = ~{projected}"
               if rep.stats["placeholders"] else f"{words} words")
        add("warn", "length", f"{how} (target {lo_w}-{hi_w})")

    # banned phrases (errors); normalise curly apostrophes so ’ and ' match
    low = md.lower().replace("’", "'")
    for phrase in sorted(set(cfg["banned_phrases"]) | set(voice_banned())):
        if re.search(rf"(?<![a-z]){re.escape(phrase)}(?![a-z])", low):
            add("error", "banned-phrase", f'"{phrase}"')

    # structure
    if not p["title"]:
        add("error", "title", "missing `# Title` line")
    else:
        lo, hi = cfg["title_chars"]
        if not lo <= len(p["title"]) <= hi:
            add("warn", "title", f"{len(p['title'])} chars (want {lo}-{hi})")
        if re.search(r"\b[A-Z][a-z]+\b(\s+\b[A-Z][a-z]+\b){3,}", p["title"]):
            add("warn", "title-case", "looks like Title Case; house style is sentence case")
    if not p["subtitle"]:
        add("warn", "subtitle", "missing italic subtitle line under the title")
    else:
        lo, hi = cfg["subtitle_chars"]
        if not lo <= len(p["subtitle"]) <= hi:
            add("warn", "subtitle", f"{len(p['subtitle'])} chars (want {lo}-{hi})")
    for level, text in p["headings"]:
        if level not in cfg["heading_levels_allowed"]:
            add("error", "heading-level", f"h{level} '{text[:40]}' (Medium supports ## and ### only)")

    if ai:
        for para in p["paragraphs"]:
            unquoted = re.sub(r'"[^"]*"|“[^”]*”', "", PLACEHOLDER.sub("", para))  # quoted examples are fine
            m = FIRST_PERSON.search(unquoted)
            if m:
                add("error", "ai-first-person",
                    f"'{m.group(0)}' outside a [[HUMAN]] slot: the writer's experience must come from a slot")
        lo_s, hi_s = config.settings()["story"]["human_slots"]
        if not lo_s <= rep.stats["placeholders"] <= hi_s:
            add("warn", "slot-count", f"{rep.stats['placeholders']} [[HUMAN]] slots (want {lo_s}-{hi_s})")

    # paragraphs and sentences
    if p["paragraphs"] and re.match(r"(picture|imagine)\b", p["paragraphs"][0], re.I):
        add("warn", "opening", "opens with an invented scene; use a real observation or your own moment")
    for para in p["paragraphs"]:
        n = len(PLACEHOLDER.sub("", para).split())
        if n > cfg["paragraph_max_words"]:
            add("warn", "paragraph-length", f"{n} words: '{para[:50]}...'")
    one_liners = sum(1 for para in p["paragraphs"] if len(_sentences(para)) == 1 and len(para.split()) <= 12)
    if one_liners > cfg["one_line_paragraphs_max"]:
        add("warn", "one-liners", f"{one_liners} one-line paragraphs (max {cfg['one_line_paragraphs_max']})")
    lo, hi = cfg["sentence_avg_words"]
    if words > 200 and not lo <= rep.stats["sentence_avg"] <= hi:
        add("warn", "sentence-average", f"{rep.stats['sentence_avg']} words (want {lo}-{hi})")
    for s in sents:
        if len(s.split()) > cfg["sentence_max_words"]:
            add("warn", "sentence-length", f"{len(s.split())} words: '{s[:50]}...'")

    # tics
    if words:
        dashes = md.count("—") + len(re.findall(r"\s--\s", md))
        per150 = dashes / words * 150
        if per150 > cfg["em_dash_per_150_words_max"]:
            add("warn", "em-dash", f"{dashes} em dashes ({per150:.1f} per 150 words)")
        filler = sum(len(re.findall(rf"\b{w}\b", plain, re.I)) for w in cfg["filler_words"])
        per1000 = filler / words * 1000
        if per1000 > cfg["filler_per_1000_words_max"]:
            add("warn", "filler", f"{filler} filler words ({per1000:.1f} per 1000)")
    for i, sec in enumerate(p["sections"]):
        bolds = sum(len(re.findall(r"\*\*[^*]+\*\*", para)) for para in sec)
        if bolds > cfg["bold_per_section_max"]:
            add("warn", "bold", f"section {i}: {bolds} bold phrases")
    for n in p["list_runs"]:
        if n > cfg["list_items_max"]:
            add("warn", "list-length", f"list of {n} items (max {cfg['list_items_max']})")
    if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", md):
        add("warn", "emoji", "emoji found")
    if cfg.get("spelling") == "british":
        for us, uk in US_SPELLINGS.items():
            if re.search(rf"\b{us}(s|ed|ing|er|ers)?\b", plain, re.I) and us not in ("program", "license"):
                add("warn", "spelling", f"'{us}' -> '{uk}'")
    if re.search(r"\bclick here\b", low):
        add("warn", "links", "'click here' link text")
    return rep
