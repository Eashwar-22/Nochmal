"""Generate cached ElevenLabs audio for one unpublished staged A1 lesson."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import wave
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGED_LESSONS_ROOT = PROJECT_ROOT / "curriculum" / "a1_staging" / "lessons"
OUTPUT_ROOT = PROJECT_ROOT / "assets" / "audio" / "a1_staging"
MODEL_ID = "eleven_v4"
SAMPLE_RATE = 44_100
SAMPLE_WIDTH_BYTES = 2
CHANNELS = 1
PAUSE_SECONDS = 0.35

# Carla Blum: professional, standard-German, educational voice available to
# this project's ElevenLabs account. Override with --voice-id when comparing.
DEFAULT_VOICE_ID = "rKiu7lQ4c5P3az3745s3"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip("'\""))


def find_lesson(draft_id: str) -> dict[str, object]:
    for path in sorted(STAGED_LESSONS_ROOT.glob("*.json")):
        records = json.loads(path.read_text(encoding="utf-8"))
        for record in records:
            if record.get("draft_id") == draft_id:
                return record
    raise ValueError(f"Unknown staged lesson: {draft_id}")


def synthesize(text: str, *, api_key: str, voice_id: str) -> bytes:
    query = urllib.parse.urlencode({"output_format": "mp3_44100_128"})
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?{query}"
    payload = json.dumps(
        {
            "text": text,
            "model_id": MODEL_ID,
            "language_code": "de",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs returned HTTP {error.code}: {detail}") from error


def write_pcm_wav(path: Path, pcm: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(CHANNELS)
        output.setsampwidth(SAMPLE_WIDTH_BYTES)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(pcm)


def convert_mp3_to_wav(mp3: bytes, output_path: Path) -> None:
    """Decode the universally available API format into app-ready PCM WAV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".mp3") as source:
        source.write(mp3)
        source.flush()
        subprocess.run(
            ["lame", "--decode", "--silent", source.name, str(output_path)],
            check=True,
        )


def read_pcm_wav(path: Path) -> bytes:
    with wave.open(str(path), "rb") as source:
        expected = (CHANNELS, SAMPLE_WIDTH_BYTES, SAMPLE_RATE)
        actual = (source.getnchannels(), source.getsampwidth(), source.getframerate())
        if actual != expected:
            raise RuntimeError(f"Unexpected WAV format for {path}: {actual}")
        return source.readframes(source.getnframes())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft_id")
    parser.add_argument("--voice-id", default=DEFAULT_VOICE_ID)
    parser.add_argument(
        "--sentence",
        type=int,
        action="append",
        help="Regenerate only this one-based sentence number (repeatable).",
    )
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()

    load_env_file(PROJECT_ROOT / ".env")
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("ELEVENLABS_API_KEY is missing")

    lesson = find_lesson(arguments.draft_id)
    sentences = lesson["sentences"]
    lesson_dir = OUTPUT_ROOT / arguments.draft_id
    sentence_paths = [
        lesson_dir / f"sentence-{index:02d}.wav"
        for index in range(1, len(sentences) + 1)
    ]

    selected_sentences = set(arguments.sentence or range(1, len(sentences) + 1))
    invalid = selected_sentences - set(range(1, len(sentences) + 1))
    if invalid:
        raise SystemExit(f"Invalid sentence number(s): {sorted(invalid)}")

    for index, (sentence, path) in enumerate(
        zip(sentences, sentence_paths, strict=True), start=1
    ):
        if index not in selected_sentences:
            continue
        if path.exists() and not arguments.force:
            print(f"Using cached {path.relative_to(PROJECT_ROOT)}")
            continue
        mp3 = synthesize(sentence["de"], api_key=api_key, voice_id=arguments.voice_id)
        convert_mp3_to_wav(mp3, path)
        print(f"Generated {path.relative_to(PROJECT_ROOT)}")

    pause = b"\x00" * round(
        SAMPLE_RATE * SAMPLE_WIDTH_BYTES * CHANNELS * PAUSE_SECONDS
    )
    clips = [read_pcm_wav(path) for path in sentence_paths]
    paragraph_pcm = pause.join(clips)
    paragraph_path = lesson_dir / "paragraph.wav"
    write_pcm_wav(paragraph_path, paragraph_pcm)

    manifest = {
        "draft_id": arguments.draft_id,
        "status": lesson["status"],
        "model_id": MODEL_ID,
        "voice_id": arguments.voice_id,
        "sample_rate": SAMPLE_RATE,
        "api_output_format": "mp3_44100_128",
        "stored_output_format": "PCM 16-bit WAV",
        "pause_seconds": PAUSE_SECONDS,
        "sentence_files": [path.name for path in sentence_paths],
        "sentence_texts": [sentence["de"] for sentence in sentences],
        "sentence_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sentence_paths
        },
        "paragraph_file": paragraph_path.name,
        "paragraph_sha256": hashlib.sha256(paragraph_path.read_bytes()).hexdigest(),
        "paragraph_assembled_from_sentence_files": True,
    }
    (lesson_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Assembled {paragraph_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
