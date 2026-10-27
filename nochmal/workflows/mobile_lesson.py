"""Prepare and install one published lesson in the static frontend."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from nochmal.content.candidates import load_candidate_artifact, load_candidate_source, source_path  # noqa: E402
from nochmal.content.course_library import compiled_published_lesson  # noqa: E402
from nochmal.content.course_paths import course_level, course_number, published_audio_root, published_root  # noqa: E402
from nochmal.content.grammar_reference import (  # noqa: E402
    columns_for_help,
    selected_column_for_help,
    table_for_help,
)
from nochmal.content.models import InflectionHelp, TAG_DESCRIPTIONS  # noqa: E402
from nochmal.validation.release import release_result  # noqa: E402
from nochmal.workflows.publish_candidate import load_passing_review, load_verified_audio  # noqa: E402


WEB = ROOT / "web"
DIST = WEB / "dist"
PREPARED = WEB / "prepared"
CATALOG = DIST / "lessons.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lesson_files(lesson_id: str) -> tuple[Path, Path]:
    course_level(lesson_id)
    source_matches = [
        path
        for path in (published_root(lesson_id) / "lessons").glob("*.json")
        if json.loads(path.read_text(encoding="utf-8")).get("id") == lesson_id
    ]
    if len(source_matches) != 1:
        raise ValueError(f"Expected exactly one published source for {lesson_id}")
    source = source_matches[0]
    audio = published_audio_root(lesson_id) / lesson_id
    if not source.is_file() or not audio.is_dir():
        raise ValueError(f"Published source or audio is missing for {lesson_id}")
    return source, audio


def checked_lesson(lesson_id: str):
    source, audio = lesson_files(lesson_id)
    result = release_result(lesson_id)
    if result["verdict"] != "pass":
        raise ValueError("Release gate failed:\n" + "\n".join(result["errors"]))
    lesson = compiled_published_lesson(lesson_id)
    if lesson is None:
        raise ValueError(f"No compiled lesson exists for {lesson_id}")
    return source, audio, lesson


def payload_for(lesson, source: Path) -> bytes:
    data = lesson.model_dump(mode="json")
    for sentence in data["sentences"]:
        for group in sentence["breakdown_groups"]:
            for item in group["items"]:
                for help_data in item["inflection_help"]:
                    help_card = InflectionHelp.model_validate(help_data)
                    help_data["reference_columns"] = columns_for_help(help_card)
                    help_data["reference_table"] = table_for_help(help_card)
                    help_data["selected_column"] = selected_column_for_help(help_card)
    payload = {
        "schema_version": 1,
        "source_sha256": digest(source),
        "tag_descriptions": TAG_DESCRIPTIONS,
        "lesson": data,
    }
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def audio_names(audio: Path) -> list[str]:
    manifest = json.loads((audio / "manifest.json").read_text(encoding="utf-8"))
    return [manifest["paragraph_file"], *manifest["sentence_files"]]


def prepare_candidate(lesson_id: str) -> None:
    """Build a local mobile preview without adding the candidate to the catalog."""
    source = load_candidate_source(lesson_id)
    artifact = load_candidate_artifact(lesson_id)
    load_passing_review(lesson_id, source)
    if artifact.lesson.audio_status != "ready":
        raise ValueError("Candidate audio is not ready")
    audio, _manifest = load_verified_audio(source)
    target = PREPARED / lesson_id
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    (target / "lesson-data.json").write_bytes(payload_for(artifact.lesson, source_path(lesson_id)))
    audio_target = target / "audio"
    audio_target.mkdir(exist_ok=True)
    for name in audio_names(audio):
        shutil.copy2(audio / name, audio_target / name)
    print(f"Prepared candidate preview at {target}")
    print(f"Serve {WEB} locally and open /dist/?preview={lesson_id}")


def prepare(lesson_id: str) -> None:
    source, audio, lesson = checked_lesson(lesson_id)
    target = PREPARED / lesson_id
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    (target / "lesson-data.json").write_bytes(payload_for(lesson, source))
    audio_target = target / "audio"
    audio_target.mkdir(exist_ok=True)
    for name in audio_names(audio):
        shutil.copy2(audio / name, audio_target / name)
    print(f"Prepared {lesson_id} at {target}")
    print(f"Preview locally: python -m http.server 8000 --directory {WEB}")
    print(f"Then open http://localhost:8000/dist/?preview={lesson_id}")


def install(lesson_id: str) -> None:
    source, audio, lesson = checked_lesson(lesson_id)
    prepared = PREPARED / lesson_id
    package = prepared / "lesson-data.json"
    if not package.is_file() or package.read_bytes() != payload_for(lesson, source):
        raise ValueError("Prepared lesson is missing or stale; run prepare again")
    for name in audio_names(audio):
        staged = prepared / "audio" / name
        if not staged.is_file() or digest(staged) != digest(audio / name):
            raise ValueError(f"Prepared audio is missing or stale: {name}")

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = catalog["lessons"]
    if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
        raise ValueError("Mobile lesson catalog is invalid")
    data_path = DIST / "lesson-data" / f"{lesson_id}.json"
    audio_path = DIST / "audio" / lesson_id
    data_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path.mkdir(parents=True, exist_ok=True)
    shutil.copy2(package, data_path)
    for name in audio_names(audio):
        shutil.copy2(prepared / "audio" / name, audio_path / name)
    entry = {
        "id": lesson_id,
        "level": lesson.level,
        "number": f"{course_level(lesson_id).upper()} · {course_number(lesson_id):02d}",
        "dataFile": f"./lesson-data/{lesson_id}.json",
        "audioDirectory": f"./audio/{lesson_id}",
        "paragraphFile": json.loads((audio / "manifest.json").read_text(encoding="utf-8"))["paragraph_file"],
    }
    entries = [existing for existing in entries if existing.get("id") != lesson_id]
    entries.append(entry)
    entries.sort(key=lambda item: item["id"])
    if digest(data_path) != digest(package):
        raise ValueError("Installed mobile lesson data does not match its prepared package")
    for name in audio_names(audio):
        if digest(audio_path / name) != digest(prepared / "audio" / name):
            raise ValueError(f"Installed mobile audio does not match its prepared clip: {name}")
    temp = CATALOG.with_suffix(".json.tmp")
    temp.write_text(json.dumps({"lessons": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, CATALOG)
    shutil.rmtree(prepared)
    print(f"Installed {lesson_id} in the local mobile frontend. Deploy web/dist separately when ready.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    for action in ("check", "prepare", "prepare-candidate", "install"):
        command = subparsers.add_parser(action)
        command.add_argument("lesson_id")
    arguments = parser.parse_args()
    if arguments.action == "check":
        checked_lesson(arguments.lesson_id)
        print(f"{arguments.lesson_id}: release gate passed")
    elif arguments.action == "prepare":
        prepare(arguments.lesson_id)
    elif arguments.action == "prepare-candidate":
        prepare_candidate(arguments.lesson_id)
    else:
        install(arguments.lesson_id)


if __name__ == "__main__":
    main()
