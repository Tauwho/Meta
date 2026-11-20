## Reader

A computer science student, or a recent graduate, who has spent most of their preparation time on algorithm practice and is wondering what actually makes an internship candidate stand out. Secondary reader: a student weighing an unglamorous internship (payments, billing, internal tools) against a more famous name. After reading, they will be able to name the specific engineering habits that money-handling systems force on you, and describe one project of their own in those terms in an interview.

## Angle

Owning one boring system that moves money, with its retries, refunds and reconciliation, teaches the judgement interviewers increasingly probe for, and it makes better interview evidence than another hundred solved practice problems.

## Title options

1. What a payments internship teaches you that a LeetCode streak cannot
2. The most useful thing I learned as an intern was how money goes missing
3. Boring systems make better interview stories
4. Retries, refunds and reconciliation: an internship lesson in judgement
5. Why I would pick the payments team again

Subtitles:

1. Practice problems prove you can solve puzzles. Systems that move money teach you to ask what happens when things go wrong twice.
2. As interviews shift towards project reasoning, the unglamorous internship may give you the better story to tell.
3. Three habits that money-handling code forces on you, and how to talk about them when someone asks about your experience.

## Outline

**Opening (no heading).** Start from the contrast: a streak counter on a practice site versus a single bug where a retry could have charged someone twice. State the point by the end of the opening: practice problems train speed on clean inputs; payments work trains judgement on messy ones, and interviews are moving towards the second.

- [[HUMAN: A specific moment from your payments work when you realised the hard part was not the code but what happens on failure or retry. What was the system (described generically), what did you notice, and what did you change? No confidential details, no employer-identifying numbers.]]

## Puzzles have one right answer; payments have failure modes
Explain the difference in kind: practice problems have defined inputs and a single correct output, while payment flows have partial failures, duplicate requests and delayed confirmations. Keep it conceptual and accurate.

## Habit one: assume every request will arrive twice
Introduce idempotency in plain language: the same operation applied twice must have the same effect as once. Why retries make this mandatory, and how it changes the way you design an endpoint.

## Habit two: never edit history, add to it
Introduce the append-only ledger and compensating entries for refunds and reversals. The general lesson for any system: auditability beats convenience.

## Habit three: trust, then reconcile
Explain reconciliation: comparing your records against the provider's or bank's, on a schedule, and treating mismatches as bugs. Generalise: production needs its own checks beyond tests.

- [[HUMAN: Your opinion with reasons: which of these three habits did you find hardest to learn, and which has changed how you write ordinary code outside payments? One concrete example if you have one.]]

## How to turn this into an interview answer
Show how to describe such work as decisions and trade-offs rather than technologies. Offer a short structure (problem, failure mode, decision, what you would change) without turning it into a template.

- [[HUMAN: How you have actually described your payments work to recruiters or interviewers this season, and which framing got the better reaction. First-hand only.]]

## Ending
Land on one point: the boring team is often where you learn to think about failure, and that is the skill the newer interviews are trying to find. End with a question worth keeping, e.g. what happens in your own project if this request arrives twice.

## Claims to verify

- 2026 reporting that software engineering interviews are shifting from memorised algorithm drills towards project reasoning and evidence of how candidates work (secondary summary of Business Insider, July 2026; find the original or attribute carefully).
- Definition of idempotency and the common use of idempotency keys by payment providers (check a primary provider doc, e.g. Stripe's API documentation on idempotent requests).
- Airbnb built an idempotency framework after retries risked duplicate charges (cited in secondary 2026 write-ups; verify against Airbnb's own engineering blog before using).
- Append-only ledgers with compensating entries as standard practice for refunds and reversals (verify with at least one primary engineering source).
- Reconciliation as a scheduled comparison against processor or bank settlement data (verify wording; avoid quoting specific cadences unless sourced).

## Tags

1. Software Engineering
2. Internships
3. Payments
4. Fintech
5. Career Advice

## Target publications

1. **Level Up Coding** — accepts contributor submissions and mixes engineering explainers with career pieces, which suits a story that is both.
2. **The Startup** — wide readership interested in careers in tech; the argument about choosing unglamorous teams travels beyond engineers.
3. **Better Programming** — engineering-focused audience that values concrete design lessons such as idempotency and ledgers; check whether it is currently accepting submissions.

Check each publication's current submission guidelines before pitching; policies change and some publications pause submissions.