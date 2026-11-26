Write $n new Threads posts for account $account (@$handle).

Now in Vietnam: $now_vn

<persona>
$persona
</persona>

## Today's trend signals (Google Trends Vietnam, hot news, and this account's niche feeds)

$signals

## Topics this account already covered (do not repeat; a new development on the same story needs a clearly new angle and a different topic name)

$recent

## How past posts performed (lean towards what worked)

$performance

## Steps

1. Pick $n topics that fit the persona's niche and that people feel something about right now: a niche story from the signals, a general trend with a genuine niche angle (no forced links), or a timeless relatable situation the signals remind you of. Safe under the hard rules. Skip anything political or tragic.
2. Mix kinds and formats: at least 3 of 4 posts are `take`; use different formats from your instructions (caption + card, quote line, ask the crowd, relatable moment, hot take, useful list) so no two posts read the same.
3. For every `news` post, open at least one reputable source with web search/fetch and confirm the facts you use; list the URLs in `sources`. `take` posts may leave `sources` empty.
4. Write each post the way Vietnamese Threads actually sounds (see your instructions): 1-3 lines, aim 20-200 characters (lists up to 500), lowercase and loose, the persona's pronoun, natural particles, =))) over emoji, no AI tells.
5. Optional `reply`: one extra fun detail or a follow-up question, same casual voice, max 200 characters; for `news` it may say casually where it was read. Leave it empty for most `take` posts.
6. Give about half the posts a `card` (see Text cards in your instructions): max 140 characters, the screenshot-worthy line; then `text` is the question or reaction around it, not a copy.
7. Before you output, reread each post as a Vietnamese 22-year-old scrolling at midnight: would you stop, reply, repost or save it, and does it sound like a person typed it on a phone? If it sounds translated or like a newspaper, rewrite it.

## Output

Only this JSON object:

{"posts": [
  {"topic": "short Vietnamese topic name",
   "kind": "take | news",
   "category": "short label inside the niche, e.g. dating, situationship, celeb-couple, debate, ai-tool, gadget",
   "why_now": "one line: what signal or feeling makes this land today",
   "text": "the post",
   "card": "",
   "reply": "",
   "sources": []}
]}
