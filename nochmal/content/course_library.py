"""Load authored and published courses without a fixed level list."""

from __future__ import annotations

import json
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

from .course_paths import (
    authored_root,
    candidate_root,
    course_identifier,
    course_level,
    discovered_levels,
    level_sort_key,
    published_root,
)
from .lesson_compiler import compile_lesson
from .models import Lesson
from .source_models import CourseLessonSource


def _records_in(directory: Path) -> list[CourseLessonSource]:
    records: list[CourseLessonSource] = []
    if not directory.is_dir():
        return records
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = payload if isinstance(payload, list) else [payload]
        records.extend(CourseLessonSource.model_validate(entry) for entry in entries)
    return sorted(records, key=lambda record: record.sequence)


def _candidate_records(level: str) -> list[CourseLessonSource]:
    """Read legacy records stored one candidate directory per lesson."""

    records: list[CourseLessonSource] = []
    for path in sorted(candidate_root(level).glob("*/lesson-source.json")):
        records.append(CourseLessonSource.model_validate_json(path.read_text(encoding="utf-8")))
    return sorted(records, key=lambda record: record.sequence)


def authored_records(level: str) -> list[CourseLessonSource]:
    """Return course records, with legacy candidate records as a fallback."""

    records = _records_in(authored_root(level) / "lessons")
    if records:
        return records
    return _candidate_records(level)


def published_records(level: str) -> list[CourseLessonSource]:
    return _records_in(published_root_for_level(level) / "lessons")


def published_root_for_level(level: str) -> Path:
    return published_root(course_identifier(level, 1))


def preceding_published_targets(level: str) -> list[str]:
    targets: list[str] = []
    for previous in discovered_levels():
        if level_sort_key(previous) >= level_sort_key(level):
            break
        for lesson in published_lessons(previous):
            targets.extend(lesson.new_targets)
    return targets


def compile_records(
    records: Iterable[CourseLessonSource], *, introduced_targets: Iterable[str]
) -> list[Lesson]:
    targets = list(introduced_targets)
    lessons: list[Lesson] = []
    for record in sorted(records, key=lambda item: item.sequence):
        lessons.append(compile_lesson(record.model_dump(mode="json"), targets))
        targets.extend(record.new_targets)
    return lessons


def course_lessons(level: str) -> list[Lesson]:
    return compile_records(
        authored_records(level),
        introduced_targets=preceding_published_targets(level),
    )


@lru_cache(maxsize=None)
def _published_lesson_tuple(level: str) -> tuple[Lesson, ...]:
    """Compile a level's published lessons once per Python process."""
    records = published_records(level)
    if not records:
        return ()
    prior_targets = preceding_published_targets(level)
    # A released lesson may recycle targets introduced by an earlier authored
    # lesson that is still awaiting release, so compile against the complete
    # source sequence for its own level.
    all_level_records = authored_records(level) or records
    lessons: list[Lesson] = []
    for record in records:
        same_level_targets = [
            target
            for prior in all_level_records
            if prior.sequence < record.sequence
            for target in prior.new_targets
        ]
        lessons.append(
            compile_lesson(record.model_dump(mode="json"), prior_targets + same_level_targets)
        )
    return tuple(lessons)


def published_lessons(level: str) -> list[Lesson]:
    """Return a fresh list so callers cannot mutate the cached lesson set."""
    return list(_published_lesson_tuple(level))


def clear_published_lesson_cache() -> None:
    """Discard cached compiled releases after publication changes on disk."""
    _published_lesson_tuple.cache_clear()


def compiled_published_lesson(lesson_id: str) -> Lesson | None:
    return next(
        (lesson for lesson in published_lessons(course_level(lesson_id)) if lesson.id == lesson_id),
        None,
    )


def all_course_lessons() -> list[Lesson]:
    """Return every course lesson, replacing source records with releases."""

    result: list[Lesson] = []
    for level in discovered_levels():
        published = {lesson.id: lesson for lesson in published_lessons(level)}
        authored = course_lessons(level)
        if authored:
            result.extend(published.get(lesson.id, lesson) for lesson in authored)
        else:
            result.extend(published.values())
    return result
