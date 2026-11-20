Revise the story by applying the editor's fixes and the linter issues. Change only what is needed; keep what already works.

Story:
$story

Editor's fixes:
$fixes

Linter issues:
$lint

Rules:
- Keep every `[[HUMAN: ...]]` slot (you may sharpen a slot's prompt if the editor asked).
- Never invent anecdotes, quotes or numbers.
- Stay within $min_words to $max_words words.

Return only the revised Markdown.
