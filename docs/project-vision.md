# Nochmal: product vision and engineering direction

This document preserves the complete product idea and the original technical
direction for Nochmal. Operational authoring rules live separately in
[`lesson-format.md`](lesson-format.md), and current implementation status lives
in [`progress.md`](progress.md).

## Project context and working style

- Easwaran knows Python, SQL, ML, and some backend development, and prefers
  Python scripts over notebooks and unnecessarily complicated frontend work.
- The original schedule assumed roughly three hours per day, a working local
  prototype after one week, and the possibility of a small paid product after
  about two months of consistent work.
- Engineering decisions should remain understandable enough for the owner to
  explain and maintain the product independently.
- The initial cash budget was approximately €20–30, with free tiers preferred.
  Do not buy anything, start a paid service, deploy publicly, or create a
  billing account without explicit approval.
- A ChatGPT subscription does not necessarily include OpenAI API credits. API
  access should be verified without exposing secrets, and work that does not
  require an API should continue when access is unavailable.

## Product concept

Nochmal is an app for learning German through short audio pieces, not a chatbot
or a level-by-level course.

The daily promise is: **understand one piece of German today that was difficult
on the first listen**. Do not claim the app teaches faster than alternatives
until there is evidence.

### Daily learning loop

1. The learner hears a short German recording **before seeing its text** and
   answers a simple comprehension question or gives a brief account of what
   they understood.
2. The app reveals the passage sentence by sentence. For each sentence, it
   offers natural meaning, phrase-by-phrase meaning, vocabulary,
   pronunciation/listening cues, and accurate explanations of relevant
   grammar: case, prepositions, contractions, verb forms, tense, and word
   order. The learner can replay a sentence. Explanations can expand for more
   detail; they should address the entire passage without forcing every learner
   to read every detail.
3. The learner hears the **same complete recording again without the
   transcript** and checks whether they now understand it.
4. Later lessons reuse some words and structures in new contexts. Eventually
   the app estimates the learner's ability internally and selects appropriate
   material without requiring the learner to follow visible A1/A2/B1 units.

Before adding or changing lesson breakdown content, follow the mandatory
[`grammar breakdown rulebook`](grammar-breakdown-rulebook.md) and
[`lesson-format.md`](lesson-format.md).

### Example seed passage

> Gestern wollte ich mit der U-Bahn zum Vorstellungsgespräch fahren. Aber der
> Zug ist ausgefallen, deshalb musste ich ein Taxi nehmen. Zum Glück war ich
> trotzdem pünktlich.

Useful explanations include `wollte ... fahren`, `mit der U-Bahn`,
`zum = zu dem`, the compound `Vorstellungsgespräch`, `ist ausgefallen`, verb
position in `deshalb musste ich`, and `trotzdem pünktlich`. This passage is
approximately late A2/early B1; it is only an example, not a fixed level for
the eventual product.

## Initial prototype definition of done

The local prototype should support this complete flow:

- Start a short lesson and hear German with the script hidden.
- Record an initial answer to a small comprehension check. Text or a choice
  input is sufficient; microphone input is not needed.
- Reveal all sentences, open their structured breakdowns, and replay
  individual sentences.
- Replay the identical full audio with the transcript hidden, then answer a
  final comprehension check.
- Save the attempt locally so progress survives an app restart.
- Load carefully checked example lessons and validate all generated or authored
  content mechanically.
- Explain how to run the app in a short README and provide a repeatable demo
  flow.

The initial and final listen must play the **same audio bytes**. Sentence audio
clips are generated once and joined into the full passage with short pauses;
each sentence replay uses its stored clip. Generated lessons and audio should
be cached so replaying never triggers generation again.

The prototype uses a Python-first local stack:

- Streamlit for the interface;
- small Python modules for lesson content, audio, and storage;
- Pydantic for structured lesson data; and
- SQLite for local progress.

Keep learning logic outside Streamlit-specific code so it can later be reused
in a FastAPI service.

Do not prioritize subscription payments, a trained learner model, native mobile
apps, live speech recognition, or elaborate design before the listening and
understanding loop works reliably.

## Original seven-day sequence

This was the initial prototype plan and remains useful historical context.

| Day | Outcome |
| --- | --- |
| 1 | Create the Python project, run a tiny Streamlit app, and store one hand-written lesson in a clear data structure. |
| 2 | Build audio-first presentation: the recording plays while the transcript stays hidden; add the first comprehension input. |
| 3 | Build the sentence breakdown view and individual sentence replay. Make the explanations useful for one checked lesson. |
| 4 | Add structured generation for a new short passage and sentence-level analysis, with schema validation and consistency checks. |
| 5 | Add text-to-speech, save clips/full audio, and verify that the first and final full replays use the identical saved file. |
| 6 | Add the final comprehension check and SQLite attempt history. Record what was heard, answered, revealed, and replayed. |
| 7 | Run the complete flow, fix the biggest failures, document setup, and let a few willing learners try it. |

If an external API or model setup takes time, finish the learning flow using
prepared audio and hand-checked lessons first. A functional core is more
important than automated generation.

## ML engineering direction

Make real ML engineering contributions over time without pretending that an
early prototype has enough learner data to train a personalization model.

- Design an event record from the beginning: learner/lesson identifiers, item
  or sentence, first-listen answer, final answer, replay count, explanations
  opened, elapsed time, and later performance on a **different** passage reusing
  the same concepts. Avoid collecting unnecessary personal data.
- Start adaptation with explicit rules and measurable baselines. Later estimate
  the probability that a learner understands a word, structure, or audio
  segment on the first listen; use that estimate to choose content and schedule
  reviews.
- Control generation using known vocabulary and structures, a few target
  learning items, topic, desired length, and speech difficulty. Check output
  schema mechanically and linguistic claims against a small hand-reviewed set.
  JSON validity does **not** prove that the German or grammar explanation is
  correct.
- Maintain a small evaluation set of passages, reference breakdowns, and
  comprehension questions. Track explanation errors, audio mistakes, cost per
  generated lesson, and next-day comprehension of new audio.
- Compare any future learned recommender against a simple rule-based baseline
  before claiming gains.
- Keep a brief engineering log of decisions, failures, and measured results so
  the project can be explained honestly in interviews.

## Product and engineering constraints

- Favor a maintainable one-person architecture and Python scripts over
  notebooks.
- Keep API keys out of source control and logs.
- Prefer free tiers and low-cost local solutions while the product is being
  validated.
- Do not buy services, deploy publicly, or create billing accounts without an
  explicit decision.
- Do not claim grammar explanations are correct without checking them.
- Protect the core learning promise from scope creep.

## Working principles

- Keep content rules explicit and mechanically tested.
- Treat linguistic review and schema validation as separate requirements.
- Preserve the exact audio identity between first and final listens.
- Measure behavior before introducing learned personalization.
- Keep [`progress.md`](progress.md) aligned with the actual codebase.

## Collaboration protocol

The original handover also established these project-working expectations:

1. Inspect the existing project before proposing work. Prefer one concrete,
   bounded next task over a broad plan.
2. Explain the objective, why it matters, the relevant concepts, the file or
   command involved, and what successful output looks like.
3. Favor pair programming and teaching. Review attempted code, explain important
   changes plainly, and provide larger solutions when explicitly requested or
   needed to clear a blockage.
4. Keep architecture proportional to a one-person project. When several
   solutions are plausible, recommend one and state the trade-off briefly.
5. End sessions with a recap of what works, what was learned, the next task,
   and any open question. Keep `progress.md` synchronized with reality.
6. Do not use Jupyter notebooks. Keep API keys out of source control and logs,
   establish spending limits before repeated paid API calls, and do not invent
   pricing or assert that grammar is correct without checking it.
