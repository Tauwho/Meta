# AI makes my coding homework faster and my exams harder

*Research suggests AI help raises task scores more than learning. Here is what that means for how you study for an exam with no assistant.*

This semester, my assignments got quicker and my exams did not get any easier.

[[HUMAN: The moment this semester when you noticed the gap between how fast homework felt and how hard an exam felt. Which course (data structures, OS or linear algebra), what kind of question, and what you realised. No exam content that breaches course rules.]]

The assistant improved the work I handed in. It did not necessarily improve the person handing it in. And the exams I sit are increasingly designed to tell those two things apart.

This is a piece about what I think that means for a study system, written from the middle of a semester rather than the end of a degree.

## Better scores are not the same as learning

The cleanest evidence I know of comes from outside computer science. A team of researchers ran a field experiment with high-school maths students in Türkiye, published as "Generative AI Can Harm Learning" by Bastani and colleagues. Students given a GPT-4 tutor during practice did much better on the practice problems. When the tool was taken away for the exam, the group that had used the unrestricted version did worse than students who never had it. A version designed to give hints rather than answers largely avoided that drop. [Verify: confirm authors, venue, year and the exact effect sizes against the published paper before citing; do not quote percentages until checked.]

That result maps neatly onto coursework. Practice with an assistant measures what you and the tool can do together. An exam measures what you can do alone. If the tool did the part of the thinking that the exam tests, a high practice score tells you very little.

There is also research closer to programming. An article in the *International Journal of Artificial Intelligence in Education* looks at AI assistance and novice programmers. [Verify: read DOI 10.1007/s40593-025-00496-4 directly and summarise its actual question, sample and findings in one or two sentences; do not rely on secondary summaries.]

**The difference between performance and learning is the whole story.** Performance is how well you do today with whatever help is available. Learning is what is left when the help is gone.

## Debugging code you did not write is its own skill

Writing code builds a picture in your head of what each part is for. When something breaks, you debug against that picture. You know which loop was meant to stop early and which variable you were unsure about.

Code from an assistant arrives without that picture. It often looks finished and reads well. When it fails, you have to reconstruct the intent from scratch, and that is slower than fixing your own mistakes, because you are discovering the design at the same time as the bug.

Under exam conditions this gets worse. There is no assistant to ask, the clock is running, and the question may hand you code to trace or repair. A course that asks you to trace a linked list operation on paper, or to say what a system call returns in an edge case, is testing exactly the picture the assistant built for you.

Reporting on novice programmers suggests many find AI-generated code harder to debug than their own. [Verify: the evidence link for this is a news aggregator; trace it to the original study and cite that, or cut the claim.]

## Exams are moving back into the room

Courses are responding. The direction I have seen described is towards assessments where an assistant cannot help: proctored tests, handwritten or in-person coding, and oral defences where you explain your own submission. [Verify: an aggregator reports that about two-thirds of CS educators have redesigned exams in response to AI. Find the original survey, with publisher, sample size and date, or drop the figure. Add at least one named university or course policy as an example.]

An oral defence is the clearest version of the idea. If you can explain why your solution works, why you chose this data structure, and what would break with a different input, you learnt it. If you cannot, the submission was not yours in the way that matters.

[[HUMAN: Which of your own exams or assessments this semester were proctored, oral or handwritten, and how did that change the way you had to prepare? Facts only, no grading details you are not allowed to share.]]

None of this makes AI tools bad for students. It makes the old split between coursework and exams sharper. Coursework now rewards using the tool well. Exams reward having done the thinking yourself.

## What I changed in my study system

The useful question is not whether to use AI. It is which parts of studying are for producing work and which are for building the skill the exam will test.

Some work is a reasonable shortcut. Boilerplate, syntax you have forgotten, or an explanation of a compiler error after you have already tried to read it yourself. Using the assistant here saves time without taking the learning away.

Other work has to stay unassisted:

- First attempts at an algorithm, before you look at any solution.
- Tracing code by hand, line by line, with the values written down.
- Proofs and derivations, where the steps are the point.
- Explaining your own solution out loud, as if to an examiner.

A simple rule covers most of it: attempt first, then ask, then redo without help. The first attempt shows you where you are stuck. The assistant gets you unstuck. The redo is where the learning happens, because it forces you to rebuild the reasoning without the tool's version in front of you.

This mirrors the hint-only tutor in the Bastani study. The version that held back answers protected learning. You can impose the same limit on yourself by deciding in advance what you will and will not ask for.

[[HUMAN: The specific habits you changed this semester and whether they helped. For example: a rule about when you open the assistant, practising tracing by hand, timed unassisted attempts. Be honest about what did not work.]]

## Decide which practice is for learning

The assistant is good at making work look done. That is useful when the goal is the output. It is a trap when the goal is the ability to produce the output alone, under time pressure, in a room where the tool is not allowed.

So decide in advance which parts of your week are for learning, and keep the assistant out of those. Use it freely everywhere else.

[[HUMAN: Optional: one sentence on what you will do differently for your final exams this term.]]

If the assistant vanished tomorrow, which part of this week's work could you still do?