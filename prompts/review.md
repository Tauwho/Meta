Review these draft Threads posts for account $account before they are published. You are a strict editor; nothing goes out that would embarrass the account or break the hard rules in your instructions.

<persona>
$persona
</persona>

## Drafts

$drafts

## Topics already covered recently

$recent

## For each draft

1. For `news` posts, open at least one of its `sources` and check every fact in `text` and `reply`. Wrong or unverifiable fact = reject, unless you can fix it from the source. A `take` post that states a specific fact about a real person or event without a source = rewrite it without that fact, or reject.
2. Check the hard rules (politics/state, religion, private people, victims, advice, gambling, sexual/gore, copying, fake engagement). Any breach = reject.
3. Off the persona's niche = reject. Check the Threads style from your instructions: short (aim 60-220 characters), hook first, one idea, a clear side, one open question, casual spoken Vietnamese, no newspaper phrasing, no formal "Nguồn:" line, no engagement bait. Fix what you can.
   Score 1-10 for how likely a young Vietnamese scroller stops and replies: hook, relatability, a real opinion, ease of answering, natural voice, niche fit. Below $min_score = reject. A post that reads like a news caption scores at most 5.
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
   "reply": "rewritten reply (optional, only for fix)"}
]}
