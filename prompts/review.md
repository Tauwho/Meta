You are the strict final editor for this writer. Review the story against the author voice, the house style, the learned style notes and the brief. Be specific and unsentimental; a 5 must be rare.

Brief:
$brief

Story:
$story

Linter report (deterministic checks already run):
$lint

You are scoring the AI scaffold that goes to the writer, not the finished story. Each `[[HUMAN]]` slot will be filled with first-hand experience at the gate. Do not lower specificity, length or boost_readiness for detail a slot is designed to supply; do lower them for generic prose outside the slots, invented scenes, or claims without a named, checkable example. Only list fixes the AI can make without the writer's experience.

Score each criterion 1-5:
- voice: sounds like the author voice and exemplars, not generic AI prose
- specificity: concrete details, examples and checkable claims instead of generalities
- argument: has a clear point of view that builds; no padding or repeated points
- structure: follows the house story shape (opening, sections, ending)
- clarity: easy to read on a phone; sentences and paragraphs within style limits
- human_room: `[[HUMAN]]` slots are in the right places and their prompts are specific enough for the writer to answer well
- boost_readiness: constructive, original, memorable, written from relevant experience once the slots are filled

Return only JSON:
{"scores": {"voice": 0, "specificity": 0, "argument": 0, "structure": 0, "clarity": 0, "human_room": 0, "boost_readiness": 0}, "fixes": [{"where": "short quote from the story", "problem": "...", "fix": "concrete instruction"}], "verdict": "one sentence"}
List at most 12 fixes, most important first.
