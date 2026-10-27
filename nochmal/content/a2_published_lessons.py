"""Compatibility export for the second published level."""

from .course_library import published_lessons


def load_a2_published_lessons():
    return published_lessons(__name__.split(".")[-1].split("_")[0])


A2_PUBLISHED_LESSONS = load_a2_published_lessons()
