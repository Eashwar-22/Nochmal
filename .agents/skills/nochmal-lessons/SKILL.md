---
name: nochmal-lessons
description: Create, curate, audit, and release numbered Nochmal A2 lessons from the existing blueprint and authored course records. Use when the user names A2 lesson numbers or asks for the lesson pipeline, audio, publication, or deployment.
---

# Numbered A2 lesson workflow

The user supplies lesson numbers. `curriculum/a2_blueprint.md` is existing,
read-only planning input. A1 is already published. Do not choose a new topic,
rewrite the blueprint, or alter published lessons while creating or auditing.
B1 is outside this workflow until the user asks for it.

Before creating or substantially editing a lesson, read
`docs/grammar-breakdown-rulebook.md` and `docs/lesson-format.md` in full. Their
publication checklist is a release gate. Preserve staged curriculum records;
only the publication manifests expose lessons in the app.

## Create or curate requested numbers

1. Read each numbered blueprint entry and its matching record in
   `curriculum/a2_course/lessons/`. These authored records already contain
   passage text and annotations for A2 lessons 001–072. Do not overwrite one
   simply to make a candidate.
2. Run `.venv/bin/python scripts/lesson_flow.py status a2-course-NNN` and
   `prepare` for a requested unpublished number. `prepare` copies an existing
   authored record only when its candidate is absent, then compiles it.
3. Curate the candidate sentence by sentence: exact source tokens, word cards,
   useful phrase results, controlled tags, visible changes, complete verb and
   inflection help, natural translations, and blueprint fit. Put contextual
   corrections in structured lesson metadata; add reusable grammar logic only
   for a genuinely general unsupported form. Never put a whole sentence branch
   in shared code. If the German or English passage changes, update the
   matching authored A2 record as well so subsequent audio generation uses
   the exact same text. Keep the blueprint unchanged.
4. Run the candidate build and relevant tests. Leave the app and publication
   manifests untouched. Report the file paths and remaining issues.

## Chat creation and repair; command audit

Chat creates and repairs unpublished candidates. If the user pastes `release`
audit findings, fix those concrete issues in candidate metadata or passage,
synchronize the authored record, rebuild, and run focused validation. Do not
hand-write or alter `review.json` or preflight receipts.
Do not invoke a nested `codex exec` to repair a candidate; use the current chat.

The user runs `.venv/bin/python scripts/lesson_flow.py release a2-course-NNN`
after chat editing. It performs a fresh independent, read-only audit
when the source has no current passing review. It records the review bound to
the source hash. If it fails, it stops before audio and prints findings to
bring back to chat. After a chat repair, the user reruns the same `release`
command. No manual status flags or review JSON editing are needed.

If you are the read-only reviewer launched by `lesson_flow.py audit`, perform
the audit directly. Do not launch another agent or call `lesson_flow.py audit`
again. Ignore any earlier `review.json` verdict when judging the content.

## Audio and release

After a passing audit, `ready` generates or reuses ElevenLabs audio, builds the
unpublished mobile package, and runs preflight. Audio may consume ElevenLabs
credits. The package is verified by its generated-data and audio-integrity
checks; it does not require a local review prompt.

The user runs `release` after chat has created or repaired a candidate. It runs
the ready checks itself, then publishes, installs, and deploys the verified
mobile package without confirmation prompts. `publish` is the explicit change
to the app's published-lesson list.

For mobile release, run `upload` for published audio, then `mobile-prepare`,
`mobile-install`, and `deploy`. The
last step changes the live Cloudflare Pages site. A request to create or audit
lessons does not authorize these release actions; a request to release the
named lessons does.

Use `docs/lesson-workflow.md` for the exact commands and file locations. Stop
at the first failed gate, report the blocking lesson and evidence, and preserve
all other authored and staged records.
