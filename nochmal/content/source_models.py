"""Strict schemas for authored curriculum files.

The compiled UI models describe what the app renders.  These models validate
the author-owned JSON before the compiler is allowed to transform it.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import Field, model_validator

from .models import (
    PerformanceActivity,
    SentenceAnnotations,
    SpeechAlternative,
    StrictModel,
)


TOKEN_PATTERN = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)


def normalized_tokens(text: str) -> list[str]:
    return [token.casefold() for token in TOKEN_PATTERN.findall(text)]


def phrase_occurs_in_order(source: str, phrase: str) -> bool:
    """Accept contiguous phrases and ordered chunks separated by an ellipsis."""

    source_tokens = normalized_tokens(source)
    chunks = [
        normalized_tokens(chunk)
        for chunk in re.split(r"\.{3}|…", phrase)
        if normalized_tokens(chunk)
    ]
    cursor = 0
    for chunk in chunks:
        for index in range(cursor, len(source_tokens) - len(chunk) + 1):
            if source_tokens[index : index + len(chunk)] == chunk:
                cursor = index + len(chunk)
                break
        else:
            return False
    return bool(chunks)


class ComprehensionSource(StrictModel):
    question_en: str
    answer_en: str


class CourseSentenceSource(StrictModel):
    de: str
    en: str
    audio_path: str | None = None
    annotations: SentenceAnnotations = Field(default_factory=SentenceAnnotations)

    @model_validator(mode="after")
    def require_annotations_to_reference_the_sentence(self) -> "CourseSentenceSource":
        source_tokens = set(normalized_tokens(self.de))
        keyed_annotations = {
            "word_tags": self.annotations.word_tags,
            "excluded_word_tags": self.annotations.excluded_word_tags,
            "base_forms": self.annotations.base_forms,
            "word_meanings": self.annotations.word_meanings,
            "verb_meanings": self.annotations.verb_meanings,
            "verb_forms": self.annotations.verb_forms,
            "verb_components": self.annotations.verb_components,
            "spoken_forms": self.annotations.spoken_forms,
        }
        for field_name, values in keyed_annotations.items():
            missing = sorted(key for key in values if key.casefold() not in source_tokens)
            if missing:
                raise ValueError(
                    f"{field_name} keys are absent from the German sentence: {missing}"
                )

        missing_components = sorted(
            component
            for components in self.annotations.verb_components.values()
            for component in components
            if component.casefold() not in source_tokens
        )
        if missing_components:
            raise ValueError(
                "verb_components values are absent from the German sentence: "
                + ", ".join(missing_components)
            )

        occurrence_counts: dict[str, int] = {}
        for token in normalized_tokens(self.de):
            occurrence_counts[token] = occurrence_counts.get(token, 0) + 1
        invalid_occurrences = [
            f"{item.surface}#{item.occurrence}"
            for item in self.annotations.word_occurrences
            if occurrence_counts.get(item.surface.casefold(), 0) < item.occurrence
        ]
        if invalid_occurrences:
            raise ValueError(
                "word_occurrences entries are absent or out of range: "
                + ", ".join(invalid_occurrences)
            )

        phrase_fields = {
            "phrases": [item.german for item in self.annotations.phrases],
            "excluded_phrases": self.annotations.excluded_phrases,
            "excluded_phrase_tags": list(self.annotations.excluded_phrase_tags),
        }
        for field_name, phrases in phrase_fields.items():
            absent = [
                phrase
                for phrase in phrases
                if not phrase_occurs_in_order(self.de, phrase)
            ]
            if absent:
                raise ValueError(
                    f"{field_name} entries are absent or out of order: {absent}"
                )

        normalized = [
            " ".join(normalized_tokens(item.german))
            for item in self.annotations.phrases
        ]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Authored phrases must not contain duplicates")
        return self


class CourseLessonSource(StrictModel):
    id: str
    source_draft_id: str
    sequence: int
    band: str = Field(pattern=r"^[A-C][1-2](?:\.[1-2])?(?:-[A-C][1-2])?$")
    format: Literal[
        "narrative",
        "description",
        "dialogue",
        "message",
        "announcement",
        "instructions",
    ]
    title_de: str
    title_en: str
    topic: str
    communicative_goal: str
    grammar_focus: str
    supporting_structures: list[str]
    grammar_notes: list[str] = Field(default_factory=list)
    new_targets: list[str]
    recycled_targets: list[str]
    recycles_from: list[int]
    audio_path: str | None = None
    sentences: list[CourseSentenceSource]
    comprehension: ComprehensionSource
    source_basis: list[str]
    speech_alternatives: list[SpeechAlternative] = Field(default_factory=list)
    performance_activity: PerformanceActivity | None = Field(
        default=None, exclude_if=lambda value: value is None
    )

    @model_validator(mode="after")
    def require_complete_lesson(self) -> "CourseLessonSource":
        if not self.sentences:
            raise ValueError("A course lesson requires at least one sentence")
        sentence_audio = [sentence.audio_path for sentence in self.sentences]
        has_any_audio = bool(self.audio_path) or any(sentence_audio)
        has_complete_audio = bool(self.audio_path) and all(sentence_audio)
        if has_any_audio and not has_complete_audio:
            raise ValueError(
                "Lesson and sentence audio paths must either all be present or all be absent"
            )
        return self
