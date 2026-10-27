# Nochmal authored A2 course

This directory contains strict, app-shaped A2 lesson sources. These are course
lessons, not candidate preview packages. They compile through the same
`CourseLessonSource` and `Lesson` models as the reviewed A1 course.

The authored records intentionally have no audio paths. Lessons 001–012 have
separate reviewed copies in `curriculum/a2_published/` and are already visible
in the app. Lessons 013–072 remain unpublished. A new lesson becomes visible
only after its exact text receives reviewed ElevenLabs v4 audio, its review is
current, the release validator and tests pass, and the rendered lesson has been
inspected.

Course IDs run from `a2-course-001` through `a2-course-072`. Their global
`sequence` values run from 49 through 120, immediately after the 48 A1 lessons.
The source design follows `curriculum/a2_blueprint.md` and the mandatory rules
in `docs/grammar-breakdown-rulebook.md` and `docs/lesson-format.md`.
