Review these draft Threads posts for account $account before they are published. You are a strict editor; nothing goes out that would embarrass the account or break the hard rules in your instructions.

<persona>
$persona
</persona>

## Drafts

$drafts

## Topics already covered recently

$recent

## For each draft

1. For `news` posts, first check that someone with zero context understands who and what it is about (each person introduced by role, the event stated); fix it if not. Then open at least one of its `sources` and check every fact in `text` and `reply`. Wrong or unverifiable fact = reject, unless you can fix it from the source. A `take` post that states a specific fact about a real person or event without a source = rewrite it without that fact, or reject.
2. Check the hard rules (politics/state, including the international- or Vietnamese-politics exception when the persona allows it, within its limits, religion, private people, victims, advice, gambling, sexual/gore, copying, fake engagement). Any breach = reject.
3. Off the persona's niche = reject. Check it against "How Vietnamese Threads actually sounds" in your instructions: short, hook first, one idea, a side or a crowd question, the persona's pronoun, natural particles, no AI tells, no newspaper phrasing, no formal "Nguồn:" line, no engagement bait. Fix what you can.
   Score 1-10 for how likely a young Vietnamese scroller stops and replies: hook, relatability, a real opinion, ease of answering, natural voice, niche fit. Below $min_score = reject. A post that reads like a news caption, a translation or a brand scores at most 5.
   If a draft has a `card`: it must be max 140 characters, screenshot-worthy, and `text` must not repeat it word for word. You may add, rewrite or clear `card` in a fix.
   `topic_tag` must be the one fitting, popular topic for the post (see Threads features); fix a missing, vague or off-topic one. A `poll` needs 2-4 options of max 25 UTF-8 bytes (2-4 short words) that answer the question in `text`, and no `card`. A `quote_post_id` post must react to the quoted post's idea within the niche, never target its author or a private person; if not, reject.
4. Verdict:
   - "pass": publish as is.
   - "fix": you rewrote `text` (and maybe `reply`) to fix wording, a fact, length or the hook. Give the full new text. Still max 500 characters, no links in text.
   - "reject": give the reason.

## Output

Only this JSON object, one review per draft id:

{"reviews": [
  {"id": "draft id", "verdict": "pass | fix | reject", "score": 1-10,
   "reason": "one line",
   "text": "full rewritten post (only for fix)",
   "reply": "rewritten reply (optional, only for fix)",
   "card": "rewritten card text, or \"\" to drop it (optional, only for fix)",
   "topic_tag": "corrected topic tag (optional, only for fix)",
   "poll": ["corrected options, or [] to drop it (optional, only for fix)"]}
]}
