"""Build and load deterministic, unpublished lesson preview artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from .a1_a2_lessons import compile_lesson
from .a1_course_lessons import A1_COURSE_LESSONS
from .models import Lesson, StrictModel
from .ordering import ordered_breakdown_items
from .source_models import CourseLessonSource
from .validation import validate_lesson_library
from nochmal.paths import PROJECT_ROOT


CANDIDATES_ROOT = PROJECT_ROOT / "curriculum" / "a1_candidates"
ACTIVE_PREVIEWS_ROOT = PROJECT_ROOT / "data" / "lesson-previews"


class LessonCandidateArtifact(StrictModel):
    schema_version: Literal[1]
    source_sha256: str
    lesson: Lesson


def candidate_directory(lesson_id: str) -> Path:
    return CANDIDATES_ROOT / lesson_id


def source_path(lesson_id: str) -> Path:
    return candidate_directory(lesson_id) / "lesson-source.json"


def artifact_path(lesson_id: str) -> Path:
    return candidate_directory(lesson_id) / "compiled-lesson.json"


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_candidate_source(lesson_id: str) -> CourseLessonSource:
    path = source_path(lesson_id)
    if not path.is_file():
        raise ValueError(f"No lesson candidate source exists for {lesson_id!r}")
    source = CourseLessonSource.model_validate_json(path.read_text(encoding="utf-8"))
    if source.id != lesson_id:
        raise ValueError("Candidate directory and lesson source ID do not match")
    return source


def compile_candidate(source: CourseLessonSource) -> Lesson:
    introduced_targets = [
        target
        for lesson in sorted(
            A1_COURSE_LESSONS,
            key=lambda item: item.sequence if item.sequence is not None else 10_000,
        )
        if lesson.sequence is not None and lesson.sequence < source.sequence
        for target in lesson.new_targets
    ]
    return compile_lesson(source.model_dump(mode="json"), introduced_targets)


def candidate_errors(lesson_id: str, artifact: LessonCandidateArtifact) -> list[str]:
    errors: list[str] = []
    source = load_candidate_source(lesson_id)
    expected_hash = source_sha256(source_path(lesson_id))
    if artifact.source_sha256 != expected_hash:
        errors.append("candidate source changed after the compiled artifact was built")
    if artifact.lesson.id != lesson_id:
        errors.append("compiled artifact lesson ID does not match its candidate directory")

    expected_lesson = compile_candidate(source)
    if artifact.lesson.model_dump(mode="json") != expected_lesson.model_dump(mode="json"):
        errors.append("compiled artifact does not match the deterministic compiler output")
    errors.extend(validate_lesson_library([artifact.lesson]))
    return errors


def load_candidate_artifact(lesson_id: str) -> LessonCandidateArtifact:
    path = artifact_path(lesson_id)
    if not path.is_file():
        raise ValueError(
            f"No compiled candidate exists for {lesson_id!r}; build it before previewing"
        )
    artifact = LessonCandidateArtifact.model_validate_json(
        path.read_text(encoding="utf-8")
    )
    errors = candidate_errors(lesson_id, artifact)
    if errors:
        raise ValueError("\n".join(f"- {error}" for error in errors))
    return artifact


def active_preview_path(lesson_id: str) -> Path:
    return ACTIVE_PREVIEWS_ROOT / f"{lesson_id}.json"


def load_active_preview_lessons() -> tuple[Lesson, ...]:
    if not ACTIVE_PREVIEWS_ROOT.is_dir():
        return ()
    lessons: list[Lesson] = []
    for path in sorted(ACTIVE_PREVIEWS_ROOT.glob("*.json")):
        artifact = LessonCandidateArtifact.model_validate_json(
            path.read_text(encoding="utf-8")
        )
        errors = candidate_errors(artifact.lesson.id, artifact)
        if errors:
            raise ValueError(
                f"Invalid active preview {artifact.lesson.id!r}:\n"
                + "\n".join(f"- {error}" for error in errors)
            )
        lessons.append(artifact.lesson)
    return tuple(sorted(lessons, key=lambda item: item.sequence or 10_000))


def artifact_json(source: CourseLessonSource, lesson: Lesson) -> str:
    artifact = LessonCandidateArtifact(
        schema_version=1,
        source_sha256=source_sha256(source_path(source.id)),
        lesson=lesson,
    )
    return json.dumps(artifact.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n"


def preview_markdown(source: CourseLessonSource, lesson: Lesson) -> str:
    lines = [
        f"# Preview: {lesson.english_title}",
        "",
        f"- Candidate: `{lesson.id}`",
        f"- Source draft: `{source.source_draft_id}`",
        f"- Level: {lesson.level}",
        f"- Audio: {lesson.audio_status}",
        "",
        "> This file is generated before app activation. The app renders the same compiled cards.",
        "",
    ]
    for sentence_number, sentence in enumerate(lesson.sentences, start=1):
        lines.extend(
            [
                f"## Sentence {sentence_number}",
                "",
                f"**German:** {sentence.text}",
                "",
                f"**English:** {sentence.natural_meaning}",
                "",
                "| Type | German | English | Literal | Tags | Help |",
                "|---|---|---|---|---|---|",
            ]
        )
        for group in sentence.breakdown_groups:
            for item in ordered_breakdown_items(group, sentence.text):
                tags = ", ".join(tag.label for tag in item.tags) or "—"
                literal = item.literal_meaning or "—"
                help_parts: list[str] = []
                if item.verb_help:
                    help_parts.append(f"verb: {item.verb_help.infinitive}")
                help_parts.extend(
                    f"{help_.base} → {help_.surface} ({help_.case})"
                    for help_ in item.inflection_help
                )
                help_text = "; ".join(help_parts) or "—"
                cells = [
                    item.kind,
                    item.german,
                    item.english,
                    literal,
                    tags,
                    help_text,
                ]
                escaped = [cell.replace("|", "\\|") for cell in cells]
                lines.append("| " + " | ".join(escaped) + " |")
        lines.append("")
    return "\n".join(lines)
