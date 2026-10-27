"""Compatibility export for the second authored level."""

from .course_library import course_lessons


def load_a2_course_lessons():
    return course_lessons(__name__.split(".")[-1].split("_")[0])


A2_COURSE_LESSONS = load_a2_course_lessons()
