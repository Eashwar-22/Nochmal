"""Attach previously generated staged audio to an existing lesson candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from nochmal.content.candidates import (  # noqa: E402
    artifact_json,
    artifact_path,
    candidate_directory,
    compile_candidate,
    load_candidate_source,
    preview_markdown,
    source_path,
)
from nochmal.content.course_paths import (  # noqa: E402
    candidate_audio_root,
    course_level,
    source_record_for_draft,
    staged_audio_root,
)
from nochmal.content.source_models import CourseLessonSource  # noqa: E402
from nochmal.validation.models import LessonReviewReport  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def staged_record(draft_id: str) -> dict[str, object]:
    return source_record_for_draft(draft_id)


def require_matching_audio(source: CourseLessonSource) -> tuple[Path, dict[str, object]]:
    record = staged_record(source.source_draft_id)
    candidate_sentences = [{"de": item.de, "en": item.en} for item in source.sentences]
    record_sentences = record.get("sentences")
    if not isinstance(record_sentences, list):
        raise ValueError("Staged source has no sentence list")
    source_sentences = [
        {"de": sentence.get("de"), "en": sentence.get("en")}
        for sentence in record_sentences
        if isinstance(sentence, dict)
    ]
    if source_sentences != candidate_sentences:
        raise ValueError("Candidate text does not exactly match its staged course source")

    audio_dir = staged_audio_root(source.source_draft_id) / source.source_draft_id
    manifest_path = audio_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError(
            "No staged audio manifest found. Generate the audio first with "
            f"scripts/lesson_flow.py audio {source.id}"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("draft_id") != source.source_draft_id:
        raise ValueError("Staged audio manifest draft ID does not match the candidate")
    if manifest.get("model_id") != "eleven_v4":
        raise ValueError("Candidate audio must use the ElevenLabs eleven_v4 model")
    expected_texts = [item.de for item in source.sentences]
    if manifest.get("sentence_texts") != expected_texts:
        raise ValueError("Staged audio sentence text does not match the candidate")
    sentence_files = manifest.get("sentence_files")
    sentence_hashes = manifest.get("sentence_sha256")
    if not isinstance(sentence_files, list) or len(sentence_files) != len(expected_texts):
        raise ValueError("Staged audio manifest has the wrong sentence-file count")
    if not isinstance(sentence_hashes, dict):
        raise ValueError("Staged audio manifest has no sentence hashes")
    for file_name in sentence_files:
        path = audio_dir / file_name
        if not path.is_file() or sentence_hashes.get(file_name) != sha256(path):
            raise ValueError(f"Staged audio file is missing or changed: {file_name}")
    paragraph_name = manifest.get("paragraph_file")
    paragraph_hash = manifest.get("paragraph_sha256")
    if not isinstance(paragraph_name, str) or not isinstance(paragraph_hash, str):
        raise ValueError("Staged audio manifest has no paragraph hash")
    paragraph_path = audio_dir / paragraph_name
    if not paragraph_path.is_file() or paragraph_hash != sha256(paragraph_path):
        raise ValueError("Staged paragraph audio is missing or changed")
    return audio_dir, manifest


def copy_verified(source: Path, destination: Path, *, force: bool) -> None:
    if destination.exists() and sha256(destination) != sha256(source) and not force:
        raise ValueError(
            f"Refusing to replace different audio at {destination.relative_to(PROJECT_ROOT)}; "
            "use --force after reviewing it"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or sha256(destination) != sha256(source):
        with tempfile.TemporaryDirectory(prefix="nochmal-copy-", dir=destination.parent) as temporary:
            staged = Path(temporary) / destination.name
            shutil.copy2(source, staged)
            os.replace(staged, destination)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Attach verified Eleven v4 staged audio to a prebuilt candidate. No AI is called."
    )
    parser.add_argument("lesson_id")
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()

    source = load_candidate_source(arguments.lesson_id)
    if course_level(source.id) != course_level(source.source_draft_id):
        raise ValueError("Candidate and staged draft belong to different levels")
    review_path = candidate_directory(arguments.lesson_id) / "review.json"
    review: LessonReviewReport | None = None
    if review_path.is_file():
        review = LessonReviewReport.model_validate_json(
            review_path.read_text(encoding="utf-8")
        )
        if review.lesson_id != arguments.lesson_id:
            raise ValueError("Candidate review ID does not match the candidate")
        if review.source_sha256 != sha256(source_path(arguments.lesson_id)):
            raise ValueError("Candidate source changed after its review")
    staged_dir, manifest = require_matching_audio(source)
    target_dir = candidate_audio_root(arguments.lesson_id) / arguments.lesson_id
    sentence_files = manifest["sentence_files"]
    for file_name in sentence_files:
        copy_verified(staged_dir / file_name, target_dir / file_name, force=arguments.force)
    paragraph_name = manifest["paragraph_file"]
    copy_verified(staged_dir / paragraph_name, target_dir / paragraph_name, force=arguments.force)
    copy_verified(staged_dir / "manifest.json", target_dir / "manifest.json", force=arguments.force)

    source_data = json.loads(source_path(arguments.lesson_id).read_text(encoding="utf-8"))
    candidate_prefix = f"assets/audio/{course_level(arguments.lesson_id)}_candidates/{arguments.lesson_id}"
    source_data["audio_path"] = f"{candidate_prefix}/{paragraph_name}"
    for sentence, file_name in zip(source_data["sentences"], sentence_files, strict=True):
        sentence["audio_path"] = f"{candidate_prefix}/{file_name}"
    updated_source = CourseLessonSource.model_validate(source_data)
    lesson = compile_candidate(updated_source)
    source_path(arguments.lesson_id).write_text(
        json.dumps(updated_source.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if review is not None:
        rebound_review = review.model_copy(
            update={"source_sha256": sha256(source_path(arguments.lesson_id))}
        )
        review_path.write_text(
            json.dumps(rebound_review.model_dump(mode="json"), indent=2) + "\n",
            encoding="utf-8",
        )
    artifact_path(arguments.lesson_id).write_text(
        artifact_json(updated_source, lesson), encoding="utf-8"
    )
    (candidate_directory(arguments.lesson_id) / "preview.md").write_text(
        preview_markdown(updated_source, lesson), encoding="utf-8"
    )
    print(f"Attached verified audio to candidate {arguments.lesson_id}")
    print("The candidate is rebuilt and ready for a local mobile preview.")


if __name__ == "__main__":
    main()
