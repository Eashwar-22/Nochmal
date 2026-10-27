# Nochmal project instructions

## Mandatory rule for lesson work

Before creating, restructuring, integrating, publishing, or substantially
editing any lesson, read these files in full:

1. `docs/grammar-breakdown-rulebook.md`
2. `docs/lesson-format.md`

Treat the rulebook's publication checklist as a release gate. A lesson must
remain hidden from the app until its sentence-by-sentence grammar audit,
breakdown cards, visible form-change explanations, audio agreement, and tests
are complete.

Do not delete staged curriculum records merely because they are not currently
published. Preserve them in the curriculum source and expose lessons through
the app's explicit published-lesson list only after review.

Prefer reusable grammar logic and structured lesson metadata. Do not add a
literal sentence string to shared compiler code when the same requirement can
be represented by a general rule or an authored annotation in the lesson
source.

For numbered A2 lesson creation, independent Sol High audit, audio, and
release, use `.agents/skills/nochmal-lessons/SKILL.md` and the single command
entry point `scripts/lesson_flow.py`. Treat `curriculum/a2_blueprint.md` as
read-only input unless the user explicitly asks to change the blueprint.
