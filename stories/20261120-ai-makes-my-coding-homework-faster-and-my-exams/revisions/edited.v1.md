# AI makes my coding homework faster and my exams harder

*Research suggests AI help raises task scores more than learning. Here is what that means for how you study for an exam with no assistant.*

An assignment finished with an AI assistant and an exam sat without one can feel like two different courses.

[[HUMAN: The moment this semester when you noticed the gap between how fast homework felt and how hard an exam felt. Which course (data structures, OS or linear algebra), what kind of question, and what you realised. No exam content that breaches course rules.]]

The assistant improves the work you hand in. It does not necessarily improve the person handing it in. And exams are increasingly designed to tell those two things apart.

This piece is about what that means for a study system, written from the middle of a semester rather than the end of a degree.

## Better scores are not the same as learning

The cleanest evidence comes from outside computer science. Hamsa Bastani and colleagues ran a field experiment with nearly 1,000 students at a high school in Türkiye, published in *PNAS* in 2025 as ["Generative AI without guardrails can harm learning"](https://ideas.repec.org/a/nas/journl/v122y2025pe2422633122.html). Students given GPT-4 during practice did much better on the practice problems.

When the tool was taken away for the exam, the picture flipped. Students who had used a standard ChatGPT-style interface scored about 17% lower than students who never had it. A second version, designed to give hints rather than answers, left exam scores roughly where the control group's were.

The study has limits: one school, one subject, and a time when chatbots were still new. But the pattern maps neatly onto coursework. Practice with an assistant measures what you and the tool can do together. An exam measures what you can do alone. If the tool did the part of the thinking the exam tests, a high practice score tells you very little.

**The difference between performance and learning is the whole story.** Performance is how well you do today with whatever help is available. Learning is what is left when the help is gone.

## Debugging code you did not write is its own skill

Writing code builds a picture in your head of what each part is for. When something breaks, you debug against that picture. You know which loop was meant to stop early and which variable you were unsure about.

Code from an assistant arrives without that picture. It often looks finished and reads well. When it fails, you may have to reconstruct the intent from scratch, discovering the design at the same time as the bug.

[[HUMAN: One moment from your own coursework when you had to debug code an assistant wrote. What broke, how long it took, and whether it felt different from fixing your own code. Skip if you have no such moment.]]

Early research points the same way, though it does not yet settle the question. In [one study presented at ICCE 2025](https://library.apsce.net/index.php/ICCE/article/download/5679/5611/6851), students working with AI produced more advanced code but often relied on repeated prompting, while the group without AI did more of its own problem decomposition and debugging.

Under exam conditions the gap widens. There is no assistant to ask, the clock is running, and the question may hand you code to trace or repair. A course that asks you to trace a linked list operation on paper, or to say what a system call returns in an edge case, is testing exactly the picture the assistant built for you.

## Exams are moving back into the room

Courses are responding. An ACM task force on generative AI and programming assessment surveyed 763 computer science educators between May and October 2025. In [its report](https://acm-education-genai-task-force.github.io/ACM_Taskforce_GenAI_Report_16Feb26.pdf), 68% said they had adjusted how they assess students. The most common changes were proctored in-person exams, less weight on homework, oral exams and code defences, and paper-based tests.

The trend reaches beyond computer science. The Associated Press has reported on [colleges turning to oral exams](https://wtop.com/education/2026/04/perfect-homework-blank-stares-why-colleges-are-turning-to-oral-exams-to-combat-ai/) after instructors saw polished homework from students who struggled to explain it.

An oral defence is the clearest version of the idea. If you can explain why your solution works, why you chose this data structure, and what would break with a different input, you learnt it. If you cannot, the submission was not yours in the way that matters.

[[HUMAN: Which of your own exams or assessments this semester were proctored, oral or handwritten, and how did that change the way you had to prepare? Facts only, no grading details you are not allowed to share.]]

None of this makes AI tools bad for students. It makes the split between coursework and exams sharper. Coursework now rewards using the tool well. Exams reward having done the thinking yourself.

## What a study system should change

The useful question is not whether to use AI. It is which parts of studying are for producing work and which are for building the skill the exam will test.

Some work is a reasonable shortcut. Boilerplate is one. Looking up the arguments of a C library call for an operating systems lab is another, and so is asking for an explanation of a compiler error after you have already tried to read it yourself. Using the assistant here saves time without taking the learning away.

Other work has to stay unassisted:

- First attempts at an algorithm, before you look at any solution.
- Tracing code by hand, line by line, with the values written down.
- Proofs and derivations, where the steps are the point.
- Explaining your own solution out loud, as if to an examiner.

A simple rule covers most of it: attempt first, then ask, then redo without help. The first attempt shows you where you are stuck. The assistant gets you unstuck. The redo is where the learning happens, because you rebuild the reasoning without the tool's version in front of you.

This mirrors the hint-only tutor in the Bastani study. The students and subject were different, but the principle carries: the version that held back answers protected learning. You can impose the same limit on yourself by deciding in advance what you will and will not ask for.

[[HUMAN: The specific habits you changed this semester and whether they helped. For example: a rule about when you open the assistant, practising tracing by hand, timed unassisted attempts. Be honest about what did not work.]]

## Decide which practice is for learning

The assistant is good at making work look done. That is useful when the goal is the output. It is a trap when the goal is the ability to produce the output alone, under time pressure, in a room where the tool is not allowed.

[[HUMAN: Optional: one sentence on what you will do differently for your final exams this term.]]

So decide in advance which parts of your week are for learning, and keep the assistant out of those. Use it freely everywhere else.

If the assistant vanished tomorrow, which part of this week's work could you still do?