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

1. Pick $n topics that fit the persona's niche and are big right now: a niche story from the signals, or a general trend you can give a genuine niche angle (no forced links). They must be safe under the hard rules. Vary the angle across posts (news, debate, relatable situation, celebrity, tip). Skip anything political or tragic.
2. For each topic, open at least one reputable source with web search/fetch and confirm the key facts. Note the URLs you used.
3. Write the post: hook line, the specific detail, your angle, a question or take people will answer. Max 500 characters, aim 150-350.
4. Write the `reply`: one line of source credit plus one extra useful detail, max 300 characters.

## Output

Only this JSON object:

{"posts": [
  {"topic": "short Vietnamese topic name",
   "category": "short label inside the niche, e.g. celeb-couple, dating, debate, ai-tool, gadget",
   "why_now": "one line: what signal shows people care today",
   "text": "the post",
   "reply": "Nguồn: ... + one extra detail",
   "sources": ["https://...", "https://..."]}
]}
