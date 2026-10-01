"""Compile reviewed lessons promoted from the quarantined A1 drafts."""

from __future__ import annotations

from pathlib import Path

from .a1_a2_lessons import compile_lesson
from .models import Lesson
from .source_models import CourseLessonSource


CURRICULUM_ROOT = Path(__file__).resolve().parents[2] / "curriculum" / "a1_course"


def load_a1_course_lessons() -> list[Lesson]:
    records = [
        CourseLessonSource.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted((CURRICULUM_ROOT / "lessons").glob("*.json"))
    ]
    return [compile_lesson(record.model_dump(mode="json"), []) for record in records]


A1_COURSE_LESSONS = load_a1_course_lessons()
