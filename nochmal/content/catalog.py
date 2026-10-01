"""Publication catalog kept outside the Streamlit presentation layer."""

from __future__ import annotations

from pathlib import Path

from .models import Lesson, StrictModel


CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "curriculum"
    / "a1_course"
    / "publication.json"
)


class PublicationCatalog(StrictModel):
    published_lesson_ids: tuple[str, ...]
    speaking_practice_lesson_ids: frozenset[str]


def load_publication_catalog() -> PublicationCatalog:
    return PublicationCatalog.model_validate_json(
        CATALOG_PATH.read_text(encoding="utf-8")
    )


def published_lessons(lessons: list[Lesson]) -> tuple[Lesson, ...]:
    """Return manifest lessons in order, only after the release gate passes."""

    catalog = load_publication_catalog()
    by_id = {lesson.id: lesson for lesson in lessons}
    missing = [lesson_id for lesson_id in catalog.published_lesson_ids if lesson_id not in by_id]
    if missing:
        raise ValueError(f"Publication manifest references unknown lessons: {missing}")
    # Imported here to avoid making the content package depend on validation
    # while its lesson modules are still being initialized.
    from nochmal.validation.release import assert_lesson_release_ready

    for lesson_id in catalog.published_lesson_ids:
        assert_lesson_release_ready(lesson_id)
    return tuple(by_id[lesson_id] for lesson_id in catalog.published_lesson_ids)
