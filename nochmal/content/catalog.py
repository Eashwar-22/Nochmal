"""Source of truth for published mobile lessons."""

from __future__ import annotations

from .models import Lesson, StrictModel
from .course_paths import discovered_levels, published_root


class PublicationCatalog(StrictModel):
    published_lesson_ids: tuple[str, ...]


def load_publication_catalog() -> PublicationCatalog:
    published: tuple[str, ...] = ()
    for level in discovered_levels():
        path = published_root(f"{level}-course-001") / "publication.json"
        if path.is_file():
            catalog = PublicationCatalog.model_validate_json(path.read_text(encoding="utf-8"))
            published += catalog.published_lesson_ids
    if len(published) != len(set(published)):
        raise ValueError("Publication catalogs contain duplicate lesson IDs")
    return PublicationCatalog(published_lesson_ids=published)


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
