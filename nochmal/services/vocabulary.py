"""Derive a categorized vocabulary list from authored lesson breakdowns."""

from __future__ import annotations

from dataclasses import dataclass

from nochmal.content.models import BreakdownItem, Lesson


CATEGORY_ORDER = (
    "Nouns",
    "Verbs",
    "Adjectives",
    "Adverbs",
    "Pronouns",
    "Prepositions",
    "Connectors",
    "Other words",
)


@dataclass(frozen=True)
class VocabularyEntry:
    german: str
    english: str
    category: str
    tags: tuple[str, ...]


def category_for_item(item: BreakdownItem) -> str:
    labels = {tag.label for tag in item.tags}
    categories = {tag.category for tag in item.tags}

    if "noun" in labels or "noun" in categories:
        return "Nouns"
    if item.verb_help or "verb" in categories or "tense" in categories:
        return "Verbs"
    if "adjective" in labels:
        return "Adjectives"
    if "adverb" in labels or categories & {"time"}:
        return "Adverbs"
    if "personal pronoun" in labels or "possessive" in labels:
        return "Pronouns"
    if "preposition" in labels:
        return "Prepositions"
    if labels & {"conjunction", "connector", "coordinating", "subordinating"}:
        return "Connectors"
    return "Other words"


def vocabulary_for_lesson(lesson: Lesson) -> list[VocabularyEntry]:
    """Return unique reusable words in their first lesson appearance order."""
    entries: list[VocabularyEntry] = []
    seen: set[str] = set()

    for sentence in lesson.sentences:
        for group in sentence.breakdown_groups:
            for item in group.items:
                if item.kind != "word":
                    continue
                key = item.german.casefold().strip()
                if key in seen:
                    continue
                seen.add(key)
                entries.append(
                    VocabularyEntry(
                        german=item.german,
                        english=item.english,
                        category=category_for_item(item),
                        tags=tuple(tag.label for tag in item.tags),
                    )
                )
    return entries


def grouped_vocabulary(lesson: Lesson) -> dict[str, list[VocabularyEntry]]:
    return group_entries(vocabulary_for_lesson(lesson))


def vocabulary_for_lessons(lessons: list[Lesson]) -> list[VocabularyEntry]:
    entries: list[VocabularyEntry] = []
    seen: set[str] = set()
    for lesson in lessons:
        for entry in vocabulary_for_lesson(lesson):
            key = entry.german.casefold().strip()
            if key not in seen:
                seen.add(key)
                entries.append(entry)
    return entries


def group_entries(
    entries: list[VocabularyEntry],
) -> dict[str, list[VocabularyEntry]]:
    return {
        category: [entry for entry in entries if entry.category == category]
        for category in CATEGORY_ORDER
        if any(entry.category == category for entry in entries)
    }
