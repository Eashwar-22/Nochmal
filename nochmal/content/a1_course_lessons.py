"""Compile reviewed lessons promoted from the quarantined A1 drafts."""

from __future__ import annotations

import json
from pathlib import Path

from .a1_a2_lessons import _compile_lesson
from .models import Lesson


CURRICULUM_ROOT = Path(__file__).resolve().parents[2] / "curriculum" / "a1_course"


def load_a1_course_lessons() -> list[Lesson]:
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((CURRICULUM_ROOT / "lessons").glob("*.json"))
    ]
    return [_compile_lesson(record, []) for record in records]


A1_COURSE_LESSONS = load_a1_course_lessons()
