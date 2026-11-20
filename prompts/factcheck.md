Fact-check this draft. Use web search to verify every factual claim (numbers, dates, names, how something works, quotes). Ignore `[[HUMAN]]` slots and clearly-marked opinions.

Draft:
$draft

Source quality matters as much as the verdict. For each claim, search for the strongest source available, in this order:
1. **Primary**: the company's own careers or engineering pages, official documentation (e.g. an assessment platform's own docs), regulators, standards bodies, the original study or dataset.
2. **Reputable secondary**: established news outlets and trade press with named reporters, peer-reviewed or institutional research.
3. **Weak**: personal blogs, SEO guides, forums, review aggregators, newsletters, mirror sites. Use only when nothing better exists, and say so.

Prefer one primary source over several weak ones. If the story's central claim rests only on weak sources, say so in the Must fix section and suggest a named, checkable example the story could use instead.

Return Markdown with one row per claim:

| # | Claim (short) | Verdict | Source tier | Correction / note | Source URL |
|---|---|---|---|---|---|

Verdict is one of: OK, WRONG, OUTDATED, UNVERIFIABLE. Source tier is Primary, Secondary or Weak.

After the table, add:
## Must fix
Every non-OK row number, plus any central claim supported only by Weak sources, or `None`.
## Stronger sources to use
Up to 3 primary or reputable secondary URLs the edit should cite, each with one line on what it supports.
