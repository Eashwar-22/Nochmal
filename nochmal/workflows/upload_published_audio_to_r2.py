"""Upload release-validated lesson audio to the configured private R2 bucket.

This script reads credentials only from a local, ignored environment file. It
never publishes candidate or staging audio, and it defaults to a dry run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from nochmal.content.course_paths import published_audio_root, published_root  # noqa: E402
from nochmal.content.source_models import CourseLessonSource  # noqa: E402
from nochmal.validation.models import AudioManifest  # noqa: E402
from nochmal.validation.release import release_result  # noqa: E402


REQUIRED_ENVIRONMENT_KEYS = (
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "R2_ENDPOINT",
    "R2_BUCKET",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_environment(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise ValueError(f"R2 environment file is missing: {path}")

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator or not key or not value:
            raise ValueError(f"Invalid environment entry in {path.name}")
        values[key] = value

    missing = [key for key in REQUIRED_ENVIRONMENT_KEYS if not values.get(key)]
    if missing:
        raise ValueError("R2 environment file is missing: " + ", ".join(missing))
    return values


def published_source_path(lesson_id: str) -> Path:
    matches = [
        path
        for path in (published_root(lesson_id) / "lessons").glob("*.json")
        if json.loads(path.read_text(encoding="utf-8")).get("id") == lesson_id
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one published source for {lesson_id}")
    return matches[0]


def verified_audio(lesson_id: str) -> tuple[CourseLessonSource, Path, AudioManifest, list[Path]]:
    release = release_result(lesson_id)
    if release["verdict"] != "pass":
        errors = "\n".join(f"- {error}" for error in release["errors"])
        raise ValueError(f"Release gate failed for {lesson_id}:\n{errors}")

    catalog = json.loads((published_root(lesson_id) / "publication.json").read_text(encoding="utf-8"))
    if lesson_id not in catalog["published_lesson_ids"]:
        raise ValueError(f"{lesson_id} is not in the published lesson list")

    source = CourseLessonSource.model_validate_json(published_source_path(lesson_id).read_text(encoding="utf-8"))
    if source.audio_path is None or any(sentence.audio_path is None for sentence in source.sentences):
        raise ValueError(f"{lesson_id} does not have complete published audio")

    audio_directory = (PROJECT_ROOT / source.audio_path).parent
    expected_directory = published_audio_root(lesson_id) / lesson_id
    if audio_directory != expected_directory:
        raise ValueError("Published lesson audio is outside its expected published directory")

    manifest = AudioManifest.model_validate_json((audio_directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.status != "release_ready" or manifest.model_id != "eleven_v4":
        raise ValueError("Published audio manifest is not release-ready Eleven v4 audio")
    if manifest.draft_id != source.source_draft_id:
        raise ValueError("Published audio manifest draft ID does not match the lesson")
    if manifest.sentence_texts != [sentence.de for sentence in source.sentences]:
        raise ValueError("Published audio sentence text does not match the lesson")

    files = [audio_directory / manifest.paragraph_file]
    files.extend(audio_directory / file_name for file_name in manifest.sentence_files)
    expected_hashes = {
        manifest.paragraph_file: manifest.paragraph_sha256,
        **manifest.sentence_sha256,
    }
    for file_path in files:
        if not file_path.is_file():
            raise ValueError(f"Published audio file is missing: {file_path}")
        if sha256(file_path) != expected_hashes[file_path.name]:
            raise ValueError(f"Published audio hash does not match: {file_path.name}")
    return source, audio_directory, manifest, files


def aws_environment(credentials: dict[str, str]) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "AWS_ACCESS_KEY_ID": credentials["R2_ACCESS_KEY_ID"],
            "AWS_SECRET_ACCESS_KEY": credentials["R2_SECRET_ACCESS_KEY"],
            "AWS_DEFAULT_REGION": "auto",
            "AWS_EC2_METADATA_DISABLED": "true",
        }
    )
    return environment


def run_aws(arguments: list[str], credentials: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["aws", "--endpoint-url", credentials["R2_ENDPOINT"], *arguments],
        check=False,
        capture_output=True,
        text=True,
        env=aws_environment(credentials),
    )


def object_matches(
    key: str,
    digest: str,
    credentials: dict[str, str],
) -> bool:
    result = run_aws(
        ["s3api", "head-object", "--bucket", credentials["R2_BUCKET"], "--key", key, "--output", "json"],
        credentials,
    )
    if result.returncode:
        return False
    metadata = json.loads(result.stdout).get("Metadata", {})
    return metadata.get("sha256") == digest


def upload_file(
    file_path: Path,
    key: str,
    lesson_id: str,
    credentials: dict[str, str],
) -> None:
    digest = sha256(file_path)
    result = run_aws(
        [
            "s3", "cp", str(file_path), f"s3://{credentials['R2_BUCKET']}/{key}",
            "--content-type", "audio/wav",
            "--metadata", f"sha256={digest},lesson-id={lesson_id}",
            "--no-progress",
        ],
        credentials,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown AWS CLI error"
        raise RuntimeError(f"R2 upload failed for {file_path.name}: {detail}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload only release-validated, published lesson audio to R2. Defaults to dry run."
    )
    parser.add_argument("lesson_id")
    parser.add_argument("--upload", action="store_true", help="Perform the remote upload after validation.")
    parser.add_argument("--replace", action="store_true", help="Replace remote objects whose audited hashes differ.")
    parser.add_argument("--env-file", type=Path, default=PROJECT_ROOT / ".env.r2")
    arguments = parser.parse_args()

    if shutil.which("aws") is None:
        raise RuntimeError("AWS CLI is required. Install it before uploading to R2.")

    credentials = load_environment(arguments.env_file)
    source, _audio_directory, _manifest, files = verified_audio(arguments.lesson_id)
    prefix = f"audio/{source.id}"
    planned = [(file_path, f"{prefix}/{file_path.name}") for file_path in files]

    for file_path, key in planned:
        print(f"validated {file_path.relative_to(PROJECT_ROOT)} -> r2://{credentials['R2_BUCKET']}/{key}")
    if not arguments.upload:
        print("Dry run complete. Re-run with --upload to write to R2.")
        return

    for file_path, key in planned:
        digest = sha256(file_path)
        if object_matches(key, digest, credentials):
            print(f"unchanged {key}")
            continue
        if not arguments.replace:
            existing = run_aws(
                ["s3api", "head-object", "--bucket", credentials["R2_BUCKET"], "--key", key],
                credentials,
            )
            if existing.returncode == 0:
                raise ValueError(
                    f"Remote object differs: {key}. Re-run with --replace after reviewing it."
                )
        upload_file(file_path, key, source.id, credentials)
        print(f"uploaded {key}")


if __name__ == "__main__":
    main()
