# A1 lesson candidates

Each directory is a complete unpublished lesson package prepared before it is
shown in the app:

- `lesson-source.json` contains the authored lesson analysis;
- `compiled-lesson.json` contains the exact typed cards consumed by the app;
- `preview.md` is the same card content in a human-readable review format.

Candidate creation and app activation are separate operations. The authoring
step runs:

```bash
.venv/bin/python scripts/build_lesson_candidate.py a1-course-002
```

After reviewing `preview.md`, activate the already-built artifact locally:

```bash
.venv/bin/python scripts/push_lesson.py a1-course-002
```

This command performs deterministic validation and copies the existing
artifact into the git-ignored local preview area. It does not invoke an AI,
compile new content, generate audio, or modify the production publication
manifest. Remove the local preview with:

```bash
.venv/bin/python scripts/push_lesson.py a1-course-002 --remove
```

Preview activation is not publication. A candidate remains excluded from
`curriculum/a1_course/publication.json` until its reviewed audio, semantic
report, full release gate, tests, and visual inspection are complete.
