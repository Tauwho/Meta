# What a payments internship teaches you that a LeetCode streak cannot

*Practice problems prove you can solve puzzles. Systems that move money teach you to ask what happens when things go wrong twice.*

A streak counter on a practice site tells you how many days in a row you solved a problem. It says nothing about what you would do if the same request reached your server twice and a customer was charged twice for one order.

[[HUMAN: A specific moment from your payments work when you realised the hard part was not the code but what happens on failure or retry. What was the system (described generically), what did you notice, and what did you change? No confidential details, no employer-identifying numbers.]]

Practice problems train speed on clean inputs. Payments work trains judgement on messy ones. When an interviewer asks you to walk through a project, it is the second they are probing.

[[HUMAN: Optional one sentence on what you have noticed in your own interviews this season, if it supports this. If you keep the claim about interviews shifting, it needs a source: the brief points to Business Insider reporting from July 2026, which should be checked against the original article before it is cited.]]

## Puzzles have one right answer; payments have failure modes

A practice problem is a closed world. The inputs are defined, the constraints are stated, and there is one correct output. You either pass the hidden test cases or you do not.

A payment flow is an open one. Your service calls a provider, the network drops, and you do not know whether the charge went through. The provider may confirm it seconds later, hours later, or in a settlement file the next day. A user may press the button again because the spinner looked stuck.

None of these are edge cases in the puzzle sense. They are the normal operating conditions of a system that talks to other systems over a network. The question stops being "what is the correct answer?" and becomes "what is the safe thing to do when I do not know the answer yet?"

**That shift, from correctness to safety under uncertainty, is the skill.** It is hard to practise on a site where every test case comes back green or red.

## Habit one: assume every request will arrive twice

The first habit money-handling code forces on you is idempotency. An operation is idempotent if doing it twice has the same effect as doing it once. Setting a balance to 100 is idempotent. Adding 100 to a balance is not.

Retries make this mandatory. If a client times out and tries again, your server has no way of knowing whether the first attempt succeeded unless you give it one. The common answer is an idempotency key: the client generates a unique value for each logical operation and sends it with every attempt. The server stores the result against that key and, on a repeat, returns the stored result instead of doing the work again.

This is a standard pattern. [Stripe's API documentation on idempotent requests](https://docs.stripe.com/api/idempotent_requests) describes this mechanism for its POST requests, with the key passed in an `Idempotency-Key` header. In 2019, Airbnb's engineering team wrote about [avoiding double payments in a distributed payments system](https://medium.com/airbnb-engineering/avoiding-double-payments-in-a-distributed-payments-system-2981f6b070bb), describing Orpheus, a general-purpose idempotency library shared across its payments services.

Once you have designed one endpoint this way, you start asking the same question of every endpoint. What happens if this arrives twice? What if the second copy arrives while the first is still running? The answer changes how you design the database write, where you put the lock, and what you return to the caller.

## Habit two: never edit history, add to it

The second habit is the append-only ledger. In many payment systems, you do not change a past record to correct it. A refund is not an edit that sets the original charge to zero. It is a new entry that moves money in the opposite direction, sometimes called a compensating entry or a reversal. Modern Treasury, which builds ledger software, explains [why posted ledger entries should be immutable](https://www.moderntreasury.com/journal/enforcing-immutability-in-your-double-entry-ledger) and corrected only by later entries.

The reason is auditability. If you can overwrite a row, you lose the answer to "what did we believe at 3pm yesterday, and why?" When money is involved, someone will eventually ask that question, and "the row says zero now" is not an answer.

The general lesson travels well beyond payments. **Systems that record what happened are easier to trust than systems that only record the current state.** Event logs, audit tables and soft deletes are all versions of the same idea. Convenience says update the row. Auditability says write a new one.

## Habit three: trust, then reconcile

The third habit is reconciliation. Your database says one thing. The payment provider's records, or the bank's settlement data, say another. Reconciliation is the scheduled job that compares the two and flags every mismatch. Stripe's [bank reconciliation documentation](https://docs.stripe.com/reconciliation) shows the provider side of this: payouts are matched against bank deposits and marked reconciled or unreconciled.

What matters is the attitude it builds. A mismatch is treated as a bug, even when every test passed and no error was logged. Tests check that your code does what you expected. Reconciliation checks that the world agrees with your code. Those are different questions, and production needs both.

Outside payments, the same instinct shows up as data-quality checks, invariant monitors and the plain habit of counting things two ways and seeing whether they match.

[[HUMAN: Your opinion with reasons: which of these three habits did you find hardest to learn, and which has changed how you write ordinary code outside payments? One concrete example if you have one.]]

## How to turn this into an interview answer

The mistake most candidates make with this kind of experience is listing technologies. "I worked on the payments service using Java, PostgreSQL and Kafka" tells the interviewer what was on your screen. It does not tell them how you think.

Describe the work as a decision instead. A shape that tends to hold up:

1. **The problem.** What the system had to do, in one or two sentences, without confidential detail.
2. **The failure mode.** What could go wrong: a retry, a timeout, a late confirmation, a mismatch.
3. **The decision.** What you or the team chose to do about it, and what you gave up.
4. **What you would change.** One honest thing you would do differently now.

This is a structure, not a script. The point is that each step invites a follow-up question you can answer from experience. An interviewer who asks "why not just lock the row?" is giving you the chance to show the trade-off you already thought about.

It also answers the secondary reader's worry. A famous name on a résumé starts a conversation. A specific failure mode you designed around gives that conversation somewhere to go.

[[HUMAN: How you have actually described your payments work to recruiters or interviewers this season, and which framing got the better reaction. First-hand only.]]

## The boring team is where you learn about failure

Payments, billing and internal tools rarely appear on lists of dream internships. They are also where software meets consequences quickly, because a bug shows up as someone's money in the wrong place.

That pressure teaches you to think about failure before it happens. It is the judgement a hundred more practice problems will not give you, and it is what a good interviewer is trying to find when they ask about your projects.

So take one project you already have, payments or not, and ask it the question this kind of work asks every day: what happens if this request arrives twice?