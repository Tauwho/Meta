Write $n new Threads posts for account $account (@$handle).

Now in Vietnam: $now_vn

<persona>
$persona
</persona>

## Today's trend signals (Google Trends Vietnam + Vietnamese news feeds)

$signals

## Topics this account already covered (do not repeat; a new development on the same story needs a clearly new angle and a different topic name)

$recent

## How past posts performed (lean towards what worked)

$performance

## Steps

1. Pick $n topics from the signals that are big right now and safe under the hard rules. Prefer variety across categories (showbiz, sport, viral/social, tech, money/prices, food/travel, weird news). Skip anything political or tragic.
2. For each topic, open at least one reputable source with web search/fetch and confirm the key facts. Note the URLs you used.
3. Write the post: hook line, the specific detail, your angle, a question or take people will answer. Max 500 characters, aim 150-350.
4. Write the `reply`: one line of source credit plus one extra useful detail, max 300 characters.

## Output

Only this JSON object:

{"posts": [
  {"topic": "short Vietnamese topic name",
   "category": "showbiz | sport | viral | tech | money | food | travel | weird | lifestyle",
   "why_now": "one line: what signal shows people care today",
   "text": "the post",
   "reply": "Nguồn: ... + one extra detail",
   "sources": ["https://...", "https://..."]}
]}
