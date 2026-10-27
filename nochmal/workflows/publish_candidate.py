"""Promote a reviewed, audio-ready candidate into the live app."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from nochmal.content.candidates import (  # noqa: E402
    candidate_directory,
    candidate_errors,
    load_candidate_artifact,
    source_path,
)
from nochmal.content.course_paths import (  # noqa: E402
    candidate_audio_root,
    course_level,
    published_audio_root,
    published_root,
)
from nochmal.content.source_models import CourseLessonSource  # noqa: E402
from nochmal.validation.models import AudioManifest, LessonReviewReport  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_review_path(lesson_id: str) -> Path:
    return candidate_directory(lesson_id) / "review.json"


def load_passing_review(lesson_id: str, source: CourseLessonSource) -> LessonReviewReport:
    path = candidate_review_path(lesson_id)
    if not path.is_file():
        raise ValueError("Candidate has no review.json; it cannot be published")
    report = LessonReviewReport.model_validate_json(path.read_text(encoding="utf-8"))
    if report.lesson_id != lesson_id:
        raise ValueError("Candidate review ID does not match the candidate")
    if report.source_sha256 != sha256(source_path(lesson_id)):
        raise ValueError("Candidate source changed after its review")
    if report.overall_verdict != "pass":
        raise ValueError("Candidate review does not have a passing verdict")
    return report


def load_verified_audio(source: CourseLessonSource) -> tuple[Path, AudioManifest]:
    if source.audio_path is None:
        raise ValueError("Candidate has no paragraph audio")
    audio_dir = (PROJECT_ROOT / source.audio_path).parent
    expected_dir = candidate_audio_root(source.id) / source.id
    if audio_dir != expected_dir:
        raise ValueError("Candidate audio is outside its level-specific audio directory")
    manifest_path = audio_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("Candidate audio manifest is missing")
    manifest = AudioManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    if manifest.model_id != "eleven_v4":
        raise ValueError("Only ElevenLabs eleven_v4 audio can be published")
    expected_texts = [sentence.de for sentence in source.sentences]
    if manifest.draft_id != source.source_draft_id or manifest.sentence_texts != expected_texts:
        raise ValueError("Candidate audio does not match its source lesson")
    audio_files = [*manifest.sentence_files, manifest.paragraph_file]
    for file_name in audio_files:
        if not (audio_dir / file_name).is_file():
            raise ValueError(f"Candidate audio file is missing: {file_name}")
    if manifest.paragraph_sha256 != sha256(audio_dir / manifest.paragraph_file):
        raise ValueError("Candidate paragraph audio hash does not match")
    for file_name in manifest.sentence_files:
        if manifest.sentence_sha256.get(file_name) != sha256(audio_dir / file_name):
            raise ValueError(f"Candidate sentence audio hash does not match: {file_name}")
    return audio_dir, manifest


def published_source(source: CourseLessonSource, lesson_id: str, manifest: AudioManifest) -> CourseLessonSource:
    data = source.model_dump(mode="json")
    level = course_level(lesson_id)
    candidate_prefix = f"assets/audio/{level}_candidates/{lesson_id}/"
    published_prefix = f"assets/audio/{level}_published/{lesson_id}/"
    if not isinstance(data.get("audio_path"), str) or not data["audio_path"].startswith(candidate_prefix):
        raise ValueError("Candidate paragraph audio is not in its candidate audio directory")
    data["audio_path"] = published_prefix + manifest.paragraph_file
    for sentence, file_name in zip(data["sentences"], manifest.sentence_files, strict=True):
        if not isinstance(sentence.get("audio_path"), str) or not sentence["audio_path"].startswith(candidate_prefix):
            raise ValueError("Candidate sentence audio is not in its candidate audio directory")
        sentence["audio_path"] = published_prefix + file_name
    return CourseLessonSource.model_validate(data)


def copy_audio(source_dir: Path, destination_dir: Path, manifest: AudioManifest) -> None:
    destination_dir.mkdir(parents=True, exist_ok=False)
    for file_name in [*manifest.sentence_files, manifest.paragraph_file]:
        shutil.copy2(source_dir / file_name, destination_dir / file_name)
    release_manifest = manifest.model_copy(update={"status": "release_ready"})
    (destination_dir / "manifest.json").write_text(
        json.dumps(release_manifest.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish a passing candidate. This never calls AI or generates audio."
    )
    parser.add_argument("lesson_id")
    arguments = parser.parse_args()
    lesson_id = arguments.lesson_id
    level = course_level(lesson_id)
    course_root = published_root(lesson_id)
    audio_root = published_audio_root(lesson_id)

    artifact = load_candidate_artifact(lesson_id)
    errors = candidate_errors(lesson_id, artifact)
    if errors:
        raise ValueError("Candidate is invalid:\n" + "\n".join(f"- {item}" for item in errors))
    if artifact.lesson.audio_status != "ready":
        raise ValueError("Candidate audio is not ready")
    source = CourseLessonSource.model_validate_json(source_path(lesson_id).read_text(encoding="utf-8"))
    review = load_passing_review(lesson_id, source)
    candidate_audio_dir, audio_manifest = load_verified_audio(source)

    catalog_path = course_root / "publication.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    destination_source = course_root / "lessons" / f"{source.sequence:03d}.json"
    destination_review = course_root / "reviews" / f"{lesson_id}.json"
    destination_audio = audio_root / lesson_id
    replacing_existing = lesson_id in catalog["published_lesson_ids"]
    if not replacing_existing and (
        destination_source.exists() or destination_review.exists() or destination_audio.exists()
    ):
        raise ValueError("Refusing to replace an existing published lesson or audio directory")

    destination_source.parent.mkdir(parents=True, exist_ok=True)
    destination_review.parent.mkdir(parents=True, exist_ok=True)

    try:
        if replacing_existing:
            shutil.rmtree(destination_audio, ignore_errors=True)
        promoted_source = published_source(source, lesson_id, audio_manifest)
        destination_source.write_text(
            json.dumps(promoted_source.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        copy_audio(candidate_audio_dir, destination_audio, audio_manifest)
        promoted_review = review.model_copy(update={"source_sha256": sha256(destination_source)})
        destination_review.write_text(
            json.dumps(promoted_review.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        from nochmal.content.course_library import clear_published_lesson_cache

        clear_published_lesson_cache()
        from nochmal.validation import release

        release_errors = release.release_errors(lesson_id)
        if release_errors:
            raise ValueError("Release gate failed:\n" + "\n".join(f"- {item}" for item in release_errors))
    except Exception:
        destination_source.unlink(missing_ok=True)
        destination_review.unlink(missing_ok=True)
        shutil.rmtree(destination_audio, ignore_errors=True)
        raise

    if lesson_id not in catalog["published_lesson_ids"]:
        catalog["published_lesson_ids"].append(lesson_id)
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"Published {lesson_id} into curriculum/{level}_published")
    print("The lesson is published locally; prepare and install its mobile package before deployment.")


if __name__ == "__main__":
    main()
