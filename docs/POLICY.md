# Compliance guardrails

These rules exist so stories stay paywall-eligible and the account keeps its Partner Program enrollment. The pipeline enforces what it can; the rest is on the human at the gate.

## What the AI may do (allowed by Medium's AI policy)

- Research, trend scouting, idea scoring
- Outlines and briefs
- First drafts **as scaffolding** for the human to rewrite and extend
- Fact-checking with cited sources
- Grammar, spelling, readability and structure edits
- Titles, subtitles, tags, publication pitch, scheduling, analytics

## What the human must do (the gate)

1. **Original contribution.** Fill every `[[HUMAN: ...]]` slot with real experience, opinion or data from your own life/work. Do not ask an AI to fill them.
2. **Real editing.** Rewrite the draft in your own voice. The gate refuses a story whose final text is too close to the AI draft (see `gate.min_edit_ratio` in `config/pipeline.yaml`). This is a tripwire, not a loophole: the point is that the story is genuinely yours.
3. **Verify.** Check every claim flagged in `factcheck.md`. Remove anything you cannot stand behind.
4. **Publish by hand** in the Medium editor, set the paywall, add tags, submit to the target publication.
5. **Record** the URL with `medium gate done <id> --url <url>`.

## Hard rules

- Never paywall a story that skipped the gate.
- Never automate logins, posting, clapping, following, or commenting on Medium.
- Never run multiple accounts or engagement rings.
- Disclose affiliate links. Disclose AI assistance where it is material (e.g. AI-generated images: credit them).
- Images: Medium's built-in Unsplash picker, own photos, or AI images credited as such.

## If the rules change

Medium's policy has changed several times. Re-check the AI policy and paywall-eligibility pages monthly (the `scout` stage logs a reminder) and update this file and `docs/RESEARCH.md`.
