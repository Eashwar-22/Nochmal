"""Cross-record checks that every authored paragraph must pass.

Pydantic validates an individual object while it is constructed. These checks
cover relationships across a complete lesson library and rules that depend on
the source sentence or files on disk.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

from .models import BreakdownItem, Lesson
from .verb_reference import (
    english_current_forms,
    english_infinitive,
    english_present_forms,
    present_forms,
    reference_for,
)


TOKEN_PATTERN = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)
VERB_TAGS = {
    "verb",
    "modal verb",
    "auxiliary",
    "reflexive",
    "separable",
    "inseparable",
    "regular",
    "irregular",
    "infinitive",
    "past participle",
}
CONTRACTIONS = {
    "am", "ans", "aufs", "beim", "durchs", "fürs",
    "im", "ins", "ums", "vom", "zum", "zur",
}


class LessonValidationError(ValueError):
    """Raised when authored content violates the lesson contract."""


def _tokens(text: str) -> set[str]:
    return {token.casefold() for token in TOKEN_PATTERN.findall(text)}


def validate_lesson_library(
    lessons: Iterable[Lesson], *, project_root: Path | None = None
) -> list[str]:
    """Return every authoring error found in a lesson collection.

    Pass ``project_root`` in repository tests to include WAV existence and
    header checks. Omitting it keeps the validator useful in focused unit tests.
    """

    lesson_list = list(lessons)
    errors: list[str] = []
    seen_ids: set[str] = set()

    for lesson in lesson_list:
        context = f"lesson {lesson.id!r}"
        if lesson.id in seen_ids:
            errors.append(f"{context}: duplicate lesson id")
        seen_ids.add(lesson.id)

        if not lesson.initial_question.strip():
            errors.append(f"{context}: initial question is empty")
        if not lesson.sentences:
            errors.append(f"{context}: paragraph has no sentences")

        paragraph_text = " ".join(sentence.text for sentence in lesson.sentences).casefold()
        seen_alternatives: set[tuple[str, str]] = set()
        for alternative in lesson.speech_alternatives:
            pair = (
                alternative.lesson_phrase.casefold(),
                alternative.accepted_phrase.casefold(),
            )
            if not all(
                value.strip()
                for value in (
                    alternative.lesson_phrase,
                    alternative.accepted_phrase,
                    alternative.explanation,
                )
            ):
                errors.append(f"{context}: speech alternative is incomplete")
            if pair[0] not in paragraph_text:
                errors.append(
                    f"{context}: speech alternative phrase "
                    f"{alternative.lesson_phrase!r} is absent from the lesson"
                )
            if pair in seen_alternatives:
                errors.append(f"{context}: duplicate speech alternative {pair!r}")
            seen_alternatives.add(pair)

        if lesson.audio_status == "ready" and (
            not lesson.audio_path
            or any(not sentence.audio_path for sentence in lesson.sentences)
        ):
            errors.append(f"{context}: ready lesson has an empty audio path")
        if lesson.audio_status == "pending" and (
            lesson.audio_path is not None
            or any(sentence.audio_path is not None for sentence in lesson.sentences)
        ):
            errors.append(f"{context}: pending audio fields must be null")

        if project_root is not None and lesson.audio_status == "ready":
            audio_paths = [
                lesson.audio_path,
                *(sentence.audio_path for sentence in lesson.sentences),
            ]
            for relative_path in audio_paths:
                if relative_path is None:
                    continue
                audio_path = project_root / relative_path
                if not audio_path.is_file():
                    errors.append(f"{context}: missing audio file {relative_path!r}")
                elif audio_path.read_bytes()[:4] != b"RIFF":
                    errors.append(f"{context}: audio is not a WAV file: {relative_path!r}")

        for sentence in lesson.sentences:
            sentence_context = f"{context}, sentence {sentence.text!r}"
            if not sentence.text.strip():
                errors.append(f"{sentence_context}: source text is empty")
            if not sentence.natural_meaning.strip():
                errors.append(f"{sentence_context}: translation is empty")
            if not sentence.breakdown_groups:
                errors.append(f"{sentence_context}: breakdown is empty")

            source_tokens = _tokens(sentence.text)
            items = [
                item
                for group in sentence.breakdown_groups
                for item in group.items
            ]
            phrase_tokens = {
                token
                for item in items
                if item.kind == "phrase"
                for token in _tokens(item.german)
            }

            for item in items:
                item_context = f"{sentence_context}, item {item.german!r}"
                labels = {tag.label for tag in item.tags}

                if item.kind == "phrase":
                    unexpected = _tokens(item.german) - source_tokens
                    if unexpected:
                        errors.append(
                            f"{item_context}: phrase contains words absent from "
                            f"the source: {', '.join(sorted(unexpected))}"
                        )

                if item.kind == "word" and labels & VERB_TAGS:
                    help_card = item.verb_help
                    if help_card is None:
                        errors.append(f"{item_context}: verb help is missing")
                    elif (
                        not help_card.forms
                        or not help_card.infinitive.strip()
                        or not help_card.tense.strip()
                        or not help_card.usage.strip()
                        or any(
                            not form.pronoun.strip() or not form.verb.strip()
                            for form in help_card.forms
                        )
                    ):
                        errors.append(f"{item_context}: verb help is incomplete")
                    else:
                        try:
                            english_infinitive(help_card)
                            reference_for(help_card)
                            present = present_forms(help_card)
                            present_english = english_present_forms(help_card)
                            current_english = english_current_forms(help_card)
                        except ValueError as error:
                            if help_card.english:
                                try:
                                    present = present_forms(help_card)
                                    present_english = english_present_forms(help_card)
                                    current_english = english_current_forms(help_card)
                                except ValueError as embedded_error:
                                    errors.append(f"{item_context}: {embedded_error}")
                                    continue
                            else:
                                errors.append(f"{item_context}: {error}")
                                continue
                        if not (
                            len(present) == len(present_english) == 6
                            and len(help_card.forms) == len(current_english)
                        ):
                            errors.append(
                                f"{item_context}: the present table must contain "
                                "six bilingual forms and the sentence-tense table "
                                "must have matching German/English rows"
                            )

                if (
                    item.kind == "word"
                    and "article" in labels
                    and item.english.casefold() in {"a", "an", "the"}
                ):
                    errors.append(
                        f"{item_context}: compose the article into a noun phrase"
                    )

                visible_forms = {
                    item.german.casefold(),
                    *(form.casefold() for form in item.source_forms),
                }
                if "preposition" in labels and not visible_forms & phrase_tokens:
                    errors.append(
                        f"{item_context}: preposition is not shown in a phrase result"
                    )

                used_contractions = {
                    form.casefold()
                    for form in item.source_forms
                    if form.casefold() in CONTRACTIONS
                }
                missing_contractions = used_contractions - phrase_tokens
                if missing_contractions:
                    errors.append(
                        f"{item_context}: contraction is not shown in a phrase "
                        f"result: {', '.join(sorted(missing_contractions))}"
                    )

    return errors


def assert_valid_lesson_library(
    lessons: Iterable[Lesson], *, project_root: Path | None = None
) -> None:
    """Raise one readable exception containing all authoring failures."""

    errors = validate_lesson_library(lessons, project_root=project_root)
    if errors:
        raise LessonValidationError("\n".join(f"- {error}" for error in errors))
