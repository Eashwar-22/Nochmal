"""Published lesson content and its validation contract."""

import re

from .course_library import all_course_lessons, course_lessons, published_lessons


# The course corpus is the lesson library. Publication manifests select which
# reviewed records replace their authored counterparts in the app.
LESSONS = all_course_lessons()


def __getattr__(name: str):
    """Preserve older per-level imports while allowing every future level."""

    match = re.fullmatch(r"([A-Z]+\d+)_(PUBLISHED|COURSE)_LESSONS", name)
    if match is None:
        raise AttributeError(name)
    level, collection = match.groups()
    return published_lessons(level.lower()) if collection == "PUBLISHED" else course_lessons(level.lower())


__all__ = ["LESSONS"]
