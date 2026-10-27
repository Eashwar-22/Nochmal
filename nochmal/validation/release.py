"""Fail-closed release gate for reviewed lessons at any discovered level."""

from __future__ import annotations

import hashlib
import json
import wave
from collections import Counter
from pathlib import Path

from nochmal.content.course_library import compiled_published_lesson
from nochmal.content.course_paths import published_audio_root, published_root
from nochmal.content.source_models import CourseLessonSource, normalized_tokens, phrase_occurs_in_order
from nochmal.content.validation import validate_lesson_library
from nochmal.paths import PROJECT_ROOT

from .models import AudioManifest, LessonReviewReport


class ReleaseGateError(ValueError):
    """Raised when a lesson does not have complete, passing release evidence."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _audio_errors(source: CourseLessonSource) -> list[str]:
    errors: list[str] = []
    if source.audio_path is None:
        return ["audio: the lesson has no paragraph audio path"]

    audio_root = (PROJECT_ROOT / source.audio_path).parent
    expected_audio_root = published_audio_root(source.id) / source.id
    if audio_root != expected_audio_root:
        return ["audio: paragraph path is outside this lesson's published audio directory"]
    manifest_path = audio_root / "manifest.json"
    if not manifest_path.is_file():
        return [f"audio: missing manifest {manifest_path.relative_to(PROJECT_ROOT)}"]
    try:
        manifest = AudioManifest.model_validate_json(
            manifest_path.read_text(encoding="utf-8")
        )
    except ValueError as error:
        return [f"audio: invalid manifest: {error}"]

    expected_texts = [sentence.de for sentence in source.sentences]
    if manifest.draft_id != source.source_draft_id:
        errors.append("audio: manifest draft ID does not match the lesson source")
    if manifest.status != "release_ready":
        errors.append("audio: manifest status must be release_ready")
    if manifest.model_id != "eleven_v4":
        errors.append("audio: release audio must use ElevenLabs model eleven_v4")
    if manifest.sentence_texts != expected_texts:
        errors.append("audio: manifest sentence text does not exactly match the lesson")
    if len(manifest.sentence_files) != len(expected_texts):
        errors.append("audio: sentence file count does not match the lesson")
    if source.audio_path != (audio_root / manifest.paragraph_file).relative_to(PROJECT_ROOT).as_posix():
        errors.append("audio: paragraph path does not match the manifest")
    for sentence, file_name in zip(source.sentences, manifest.sentence_files):
        expected_path = (audio_root / file_name).relative_to(PROJECT_ROOT).as_posix()
        if sentence.audio_path != expected_path:
            errors.append(f"audio: sentence path does not match the manifest: {file_name}")
    if not manifest.paragraph_assembled_from_sentence_files:
        errors.append("audio: paragraph must be assembled from the sentence files")

    sentence_pcm: list[bytes] = []
    audio_shape: tuple[int, int, int] | None = None
    for file_name in manifest.sentence_files:
        path = audio_root / file_name
        expected_hash = manifest.sentence_sha256.get(file_name)
        if not path.is_file():
            errors.append(f"audio: missing sentence file {file_name}")
            continue
        if expected_hash is None or _sha256(path) != expected_hash:
            errors.append(f"audio: hash mismatch for {file_name}")
        try:
            with wave.open(str(path), "rb") as source_wav:
                shape = (
                    source_wav.getnchannels(),
                    source_wav.getsampwidth(),
                    source_wav.getframerate(),
                )
                if source_wav.getcomptype() != "NONE":
                    errors.append(f"audio: {file_name} is not uncompressed PCM")
                if audio_shape is None:
                    audio_shape = shape
                elif shape != audio_shape:
                    errors.append("audio: sentence WAV formats do not match")
                sentence_pcm.append(source_wav.readframes(source_wav.getnframes()))
        except (EOFError, wave.Error) as error:
            errors.append(f"audio: invalid WAV {file_name}: {error}")

    paragraph_path = audio_root / manifest.paragraph_file
    if not paragraph_path.is_file():
        errors.append(f"audio: missing paragraph file {manifest.paragraph_file}")
    else:
        if _sha256(paragraph_path) != manifest.paragraph_sha256:
            errors.append("audio: paragraph hash mismatch")
        try:
            with wave.open(str(paragraph_path), "rb") as paragraph_wav:
                paragraph_shape = (
                    paragraph_wav.getnchannels(),
                    paragraph_wav.getsampwidth(),
                    paragraph_wav.getframerate(),
                )
                paragraph_pcm = paragraph_wav.readframes(paragraph_wav.getnframes())
            if audio_shape and paragraph_shape != audio_shape:
                errors.append("audio: paragraph WAV format differs from sentence WAVs")
            if audio_shape and len(sentence_pcm) == len(manifest.sentence_files):
                pause = b"\x00" * round(
                    audio_shape[2]
                    * audio_shape[1]
                    * audio_shape[0]
                    * manifest.pause_seconds
                )
                if pause.join(sentence_pcm) != paragraph_pcm:
                    errors.append("audio: paragraph is not the exact sentence-file join")
        except (EOFError, wave.Error) as error:
            errors.append(f"audio: invalid paragraph WAV: {error}")
    return errors


def release_errors(lesson_id: str) -> list[str]:
    course_root = published_root(lesson_id)
    source_path = next(
        (
            path
            for path in sorted((course_root / "lessons").glob("*.json"))
            if json.loads(path.read_text(encoding="utf-8")).get("id") == lesson_id
        ),
        None,
    )
    review_path = course_root / "reviews" / f"{lesson_id}.json"
    errors: list[str] = []

    if source_path is None:
        return [f"source: no production lesson exists for {lesson_id}"]
    try:
        source = CourseLessonSource.model_validate_json(
            source_path.read_text(encoding="utf-8")
        )
    except ValueError as error:
        return [f"source: schema or annotation validation failed: {error}"]
    if source.id != lesson_id:
        errors.append("source: lesson ID does not match its release target")

    compiled = compiled_published_lesson(lesson_id)
    if compiled is None:
        errors.append("compiler: lesson was not compiled into its published course")
    else:
        errors.extend(
            f"contract: {error}"
            for error in validate_lesson_library([compiled], project_root=PROJECT_ROOT)
        )
        for sentence in compiled.sentences:
            expected = normalized_tokens(sentence.text)
            actual = [
                token.casefold()
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "word"
                for token in item.source_forms
            ]
            # A dictionary noun card may own an article and a declined noun
            # separated by an adjective (for example, ``die letzte Zahl``).
            # Token ownership must be exact, while visual order is checked by
            # the shared source-order renderer rather than this flat list.
            if Counter(actual) != Counter(expected):
                errors.append(
                    f"coverage: word cards do not map every source token once: {sentence.text!r}"
                )
            for group in sentence.breakdown_groups:
                for item in group.items:
                    if item.kind == "phrase" and not phrase_occurs_in_order(
                        sentence.text, item.german
                    ):
                        errors.append(
                            f"coverage: phrase is not linked to the source: {item.german!r}"
                        )

    if not review_path.is_file():
        errors.append("review: structured semantic review report is missing")
    else:
        try:
            review = LessonReviewReport.model_validate_json(
                review_path.read_text(encoding="utf-8")
            )
            if review.lesson_id != lesson_id:
                errors.append("review: lesson ID does not match")
            if review.source_sha256 != _sha256(source_path):
                errors.append("review: source changed after semantic review")
            if review.overall_verdict != "pass":
                errors.append("review: overall verdict is not pass")
        except ValueError as error:
            errors.append(f"review: invalid report: {error}")

    errors.extend(_audio_errors(source))
    return errors


def assert_lesson_release_ready(lesson_id: str) -> None:
    errors = release_errors(lesson_id)
    if errors:
        raise ReleaseGateError("\n".join(f"- {error}" for error in errors))


def release_result(lesson_id: str) -> dict[str, object]:
    errors = release_errors(lesson_id)
    return {
        "lesson_id": lesson_id,
        "verdict": "fail" if errors else "pass",
        "errors": errors,
    }
