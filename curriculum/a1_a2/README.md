# Nochmal A1-A2 passage curriculum

This directory contains the preserved, reviewable source records for 80 lessons.
The app currently publishes only Lessons 1–4 while the learning path is refined
lesson by lesson. `nochmal/content/a1_a2_lessons.py` still compiles the complete
curriculum into the production
`Lesson` model with ordered word definitions, selected phrase meanings, typed
grammar references, and bilingual verb cards. Audio alone is deliberately pending.

## Scope

- 80 original passages: A1.1 (1-20), A1.2 (21-37), A2.1 (38-60),
  and A2.2 (61-80).
- Adult everyday German, moving from short concrete descriptions to connected
  accounts, routine problems, reasons, comparisons, and arrangements.
- Statements, questions, requests, instructions, messages, and short quoted
  exchanges occur throughout the sequence.
- Spoken past narration prioritizes Perfekt. Prateritum is used mainly for
  `sein`, `haben`, and modal verbs where it is natural in conversation.

The corpus is compact. It is intended to provide a coherent A1-A2 learning
path, but 80 passages cannot by themselves guarantee mastery of every CEFR
skill. Speaking, writing, interaction, feedback, and assessment still require
separate learning activities.

## Files

- `sources.json`: authoritative sources and the claims we use from them.
- `sequence.json`: course-wide design constraints and review schedule.
- `lessons/*.json`: four ordered sets of twenty passages.
- `validate.py`: dependency-free structural and sequencing checks.

## Lesson record

Each lesson records:

- its level band, format, topic, and communicative goal;
- one primary grammar focus and supporting structures;
- optional internal curriculum-planning notes that are never rendered as a
  lesson-description panel;
- target lexical items introduced for deliberate study;
- target items deliberately recycled from earlier lessons;
- explicit links to earlier lessons;
- German sentences paired with natural English meanings;
- optional sentence-owned `annotations` containing controlled word tags,
  reusable base forms, and structured phrase records;
- optional accepted speaking alternatives with a short learner explanation;
- one first-listen comprehension question and answer; and
- source identifiers that justify the level scope.

`new_targets` is not a claim that every other word is already mastered. It is
the small set the lesson deliberately teaches. Articles are included with new
nouns so the future app breakdown can preserve grammatical gender.

Reviewed lessons store sentence-specific grammar only in `annotations`.
Reusable paradigms and hover layouts remain shared code; the compiler must not
add a Python branch keyed by a complete lesson sentence.

## Evidence policy

CEFR defines communicative ability, not one mandatory German grammar order.
Goethe supplies German-specific vocabulary, topics, examples, and exam task
evidence, but explicitly describes its wordlists as references rather than a
teaching sequence. Consequently:

1. CEFR and Goethe determine the outer level boundary.
2. The order inside that boundary is an internal pedagogical design decision.
3. No structure is labelled "officially A1" or "officially A2" unless the
   cited source actually makes that claim.
4. A future linguistic reviewer may move an item without changing the source
   record or silently rewriting history.

## Validation

Run:

```bash
python curriculum/a1_a2/validate.py
```

The validator checks counts, identifiers, level order, sentence and word
limits, bilingual sentence alignment, source identifiers, backward-only lesson
links, target counts, and whether every declared recycled item was introduced
earlier. These checks catch data mistakes; they do not prove linguistic
correctness.

After downloading the two official PDFs listed in `sources.json`, reproduce the
focus-vocabulary audit with a Python environment containing `pypdf`:

```bash
python curriculum/a1_a2/audit_wordlists.py \
  --a1-pdf /path/to/goethe-a1-wordlist.pdf \
  --a2-pdf /path/to/goethe-a2-wordlist.pdf
```

The audit allows common inflected forms and compound components. It verifies
that a focus target is attested in the appropriate inventory; it does not turn
the Goethe reference list into an official teaching order.
