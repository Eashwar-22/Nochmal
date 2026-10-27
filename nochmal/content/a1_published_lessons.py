"""Compatibility export for the first published level."""

from .course_library import published_lessons


def load_a1_published_lessons():
    return published_lessons(__name__.split(".")[-1].split("_")[0])


A1_PUBLISHED_LESSONS = load_a1_published_lessons()
