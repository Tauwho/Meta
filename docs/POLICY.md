# Publishing policy

The engine posts about trending topics to a Vietnamese audience. These rules keep the accounts alive and out of legal trouble. They are enforced in three places: `prompts/system.md` (hard rules the writer and reviewer follow), the review job (fact-check + reject), and code (`posts.py`: 500-character limit, no links in post text, at least one source URL, topic de-duplication, 36-hour expiry).

## Why each rule exists

| Rule | Reason |
|---|---|
| Facts checked against an opened source; sources kept per post | Vietnam fines and can prosecute spreading false information online (Cybersecurity Law 2018, Decree 15/2020 as amended, Decree 147/2024). Trend content is where false claims spread fastest. |
| No politics, state affairs, sovereignty, religion, ethnicity | Same laws; these are the highest-risk categories, and none of them are needed for reach. |
| No targeting private people, minors, victims; no appearance mockery | Meta Community Standards (bullying and harassment) and basic decency; the fastest way to get reported. |
| No medical, legal, investment, gambling, crypto or loan content | Meta regulated-goods and fraud policies; "money tips" accounts get flagged. |
| Own words only, credit the source in the reply | Copyright, and Threads ranks original commentary above reposted headlines. |
| Official Threads API only; no automated likes, follows or replies to others; the two accounts never interact | Meta's inauthentic-behaviour policy. Automating engagement or running accounts that boost each other is what gets accounts banned. |
| Human approval on by default (`publish.require_approval: true`) | Lets you see the quality and the risk level of AI-written Vietnamese before the account posts on its own. Turn it off only after a week or two of clean approvals. |
| One post per run, 150-minute gap, 07:00-23:00 Vietnam time | Looks human, stays far below the API's 250-posts-per-day limit. |

## Not allowed, ever

- Buying followers or engagement, follow-for-follow, giveaways that require follows.
- Selling or transferring the account (Instagram/Threads Terms of Use forbid it).
- Location spoofing (VPN) to make the account look Vietnam-based.
