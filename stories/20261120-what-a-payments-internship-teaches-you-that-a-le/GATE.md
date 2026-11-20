# Gate: What a payments internship teaches you that a LeetCode streak cannot

*Practice problems prove you can solve puzzles. Systems that move money teach you to ask what happens when things go wrong twice.*

## Checklist

- [ ] Copy `package/story.md` to `package/final.md`
- [ ] Fill all 5 `[[HUMAN]]` slots with your own experience (do not ask an AI to fill them)
- [ ] Rewrite in your voice (gate needs at least 25% changed vs the AI package)
- [ ] Check every non-OK row in `factcheck.md`; cut what you can't stand behind
- [ ] `medium lint 20261120-what-a-payments-internship-teaches-you-that-a-le` shows no errors on final.md
- [ ] `medium export 20261120-what-a-payments-internship-teaches-you-that-a-le` -> open `package/final.html`, select all, paste into Medium
- [ ] Cover: upload `package/cover.png` (house template) or, for a photo story, Unsplash: `card payment terminal`
- [ ] Tags: Software Engineering, Internships, Payments, Fintech, Career Advice
- [ ] Paywall ON (Partner Program)
- [ ] Submit to **Level Up Coding** (https://levelup.gitconnected.com) or publish directly
- [ ] `medium gate done 20261120-what-a-payments-internship-teaches-you-that-a-le --url <story url>`

## Slots to fill

1. [[HUMAN: A specific moment from your payments work when you realised the hard part was not the code but what happens on failure or retry. What was the system (described generically), what did you notice, and what did you change? No confidential details, no employer-identifying numbers.]]
2. [[HUMAN: One interview this season where you were asked to walk through a project rather than solve a puzzle: what the question was, and what follow-up came next. Skip this slot if you have no such moment.]]
3. [[HUMAN: Which of these three habits did you find hardest to learn, and why? Give your reasons, not just the name of the habit.]]
4. [[HUMAN: One place where one of these habits has changed how you write ordinary code outside payments. A concrete example if you have one.]]
5. [[HUMAN: How you have actually described your payments work to recruiters or interviewers this season, and which framing got the better reaction. First-hand only.]]

## Publication pitch

This piece argues that owning an unglamorous payments system teaches three engineering habits (idempotency, append-only ledgers and reconciliation) that make stronger interview evidence than practice-problem streaks. It mixes a concrete engineering explainer, with links to Stripe's and Airbnb's own write-ups, with practical advice for students describing their internship work in interviews. Please check it against your current submission guidelines; I am happy to adjust length or tags.

## Quality report (AI package)

Editor rubric average 4.0 after 2 round(s)

- voice: 4
- specificity: 4
- argument: 4
- structure: 4
- clarity: 4
- human_room: 4
- boost_readiness: 4

Open notes from the editor:

- "In my experience, payments, billing and internal tools are rarely the teams students hope to land.": Presents a first-person observation the writer has not supplied; the engine must not assert the writer's experience.
- "[[HUMAN: Which of these three habits did you find hardest to learn, and why?": Five slots at ~150 words each push the projected length to about 1,833 words, just over the 1,800 limit.
- "Take the timeout. Marking the order as failed is tempting, because it lets the user try again.": Good concrete example, but 'ask the provider what happened' is vague about how.
- "results.save(idempotency_key, result)": The prose after the code says the key must be claimed atomically before charging, but the code saves after charging; a careful reader will notice the gap.
- "If you are choosing between a famous name and the payments team, this is the trade-off.": Reads slightly abrupt after the interview structure and repeats 'trade-off' from the previous paragraph.
- "It is the judgement a hundred more practice problems will not give you.": Close echo of the opening's contrast; acceptable, but it is the third time the story makes this point.

Linter:

words 1083, ~5 min, avg sentence 14.2 words, sections 6

- [warn] length: 1083 words + 5 slot(s) x ~150 = ~1833 (target 1200-1800)
