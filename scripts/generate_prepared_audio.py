"""Generate prepared German WAV files with Qwen3-TTS on Apple Silicon."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QWEN_CACHE_DIR = PROJECT_ROOT / "data" / "qwen-mlx-cache"

# Set this before importing mlx-audio so Hugging Face keeps the model cache in
# the project rather than in a machine-wide user directory.
os.environ.setdefault("HF_HOME", str(QWEN_CACHE_DIR))

sys.path.insert(0, str(PROJECT_ROOT))

from nochmal.content import LESSONS  # noqa: E402

MODEL_ID = "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit"
PAUSE_BETWEEN_SENTENCES_SECONDS = 0.35

BASE_INSTRUCTION = (
    "A clear, warm female German narrator for adult language learners. "
    "Articulate word endings clearly and keep a natural, relaxed rhythm."
)
PACE_INSTRUCTION_BY_LEVEL = {
    "A1": "Speak slowly and clearly, with careful articulation for beginners.",
    "A1.1": "Speak slowly and clearly, with careful articulation for beginners.",
    "A1.2": "Speak slowly and clearly, with careful articulation for beginners.",
    "A2": "Speak deliberately, a little slower than conversational German.",
    "A2.1": "Speak deliberately, a little slower than conversational German.",
    "A2.2": "Speak deliberately, a little slower than conversational German.",
    "A2-B1": "Speak clearly at an unhurried pace.",
    "B1": "Speak clearly at a measured, natural pace.",
    "B1-B2": "Speak at a natural pace, with careful articulation.",
    "B2": "Speak naturally, with careful articulation.",
}


def instruction_for(level: str) -> str:
    return f"{BASE_INSTRUCTION} {PACE_INSTRUCTION_BY_LEVEL[level]}"


def synthesize_sentence(model: object, text: str, instruction: str) -> np.ndarray:
    """Create one sentence clip, keeping its exact samples for full playback."""
    result = next(
        model.generate_voice_design(
            text=text,
            language="German",
            instruct=instruction,
        )
    )
    audio = np.asarray(result.audio).squeeze()
    if audio.ndim != 1 or not len(audio):
        raise RuntimeError(f"Qwen returned invalid audio for: {text!r}")
    return audio


def write_wav(output_path: Path, audio: np.ndarray, sample_rate: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_path, audio, sample_rate, subtype="PCM_16")


def combine_sentences(
    clips: list[np.ndarray], *, sample_rate: int, pause_seconds: float
) -> np.ndarray:
    pause = np.zeros(round(sample_rate * pause_seconds), dtype=clips[0].dtype)
    combined: list[np.ndarray] = []
    for index, clip in enumerate(clips):
        combined.append(clip)
        if index < len(clips) - 1:
            combined.append(pause)
    return np.concatenate(combined)


def selected_lessons(lesson_ids: list[str] | None) -> list[object]:
    return [
        lesson for lesson in LESSONS if not lesson_ids or lesson.id in lesson_ids
    ]


def output_paths(lesson: object) -> tuple[Path, list[Path]]:
    """Resolve audio paths for both prepared and text-only lessons.

    The original lessons carry explicit paths in their Python definitions.  The
    sequenced A1-A2 lessons deliberately leave those fields empty until audio
    is authored, so use a deterministic convention for generated files.
    """
    lesson_slug = lesson.id
    full_path = PROJECT_ROOT / (
        lesson.audio_path or f"assets/audio/{lesson_slug}.wav"
    )
    sentence_paths = [
        PROJECT_ROOT
        / (
            sentence.audio_path
            or f"assets/audio/sentences/{lesson_slug}-{number}.wav"
        )
        for number, sentence in enumerate(lesson.sentences, start=1)
    ]
    return full_path, sentence_paths


def regenerate_in_isolated_processes(arguments: argparse.Namespace) -> None:
    """Render one lesson per process to release unified memory between lessons."""
    for lesson in selected_lessons(arguments.lesson):
        command = [sys.executable, str(Path(__file__).resolve()), "--lesson", lesson.id]
        if arguments.force:
            command.append("--force")
        if arguments.full_only:
            command.append("--full-only")
        if arguments.model != MODEL_ID:
            command.extend(["--model", arguments.model])
        subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default=MODEL_ID,
        help="MLX Qwen3-TTS VoiceDesign model to use.",
    )
    parser.add_argument(
        "--full-only",
        action="store_true",
        help="Regenerate only the complete lesson recordings.",
    )
    parser.add_argument(
        "--isolate-lessons",
        action="store_true",
        help="Run each lesson in its own process to minimise Apple unified-memory use.",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--lesson",
        nargs="+",
        choices=[lesson.id for lesson in LESSONS],
        help="Generate only the selected lesson IDs.",
    )
    arguments = parser.parse_args()

    QWEN_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if arguments.isolate_lessons:
        regenerate_in_isolated_processes(arguments)
        return

    from mlx_audio.tts.utils import load_model

    model = load_model(arguments.model)
    sample_rate = model.sample_rate
    generated = 0

    for lesson in selected_lessons(arguments.lesson):
        full_path, sentence_paths = output_paths(lesson)
        expected_paths = [full_path] if arguments.full_only else [full_path, *sentence_paths]
        if not arguments.force and all(path.exists() for path in expected_paths):
            continue

        clips = [
            synthesize_sentence(model, item.text, instruction_for(lesson.level))
            for item in lesson.sentences
        ]
        full_audio = combine_sentences(
            clips,
            sample_rate=sample_rate,
            pause_seconds=PAUSE_BETWEEN_SENTENCES_SECONDS,
        )
        write_wav(full_path, full_audio, sample_rate)
        generated += 1

        if not arguments.full_only:
            for output_path, clip in zip(sentence_paths, clips, strict=True):
                write_wav(output_path, clip, sample_rate)
                generated += 1

        print(f"Generated {lesson.id} ({len(clips)} sentences).", flush=True)

    print(f"Generated {generated} audio files with {arguments.model}.")


if __name__ == "__main__":
    main()
