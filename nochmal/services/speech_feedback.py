"""Experimental, local feedback for a learner's lesson recitation.

The service deliberately separates transcript matching from pronunciation.
Whisper can tell us which words it decoded, but it cannot reliably explain why
it decoded them or grade a learner's accent.  Pacing is similarly presented as
a broad comparison rather than as a pronunciation score.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Literal


DifferenceKind = Literal["different", "missing", "extra"]


class SpeechDependencyError(RuntimeError):
    """Raised when the optional local speech packages are unavailable."""


class SpeechAnalysisError(RuntimeError):
    """Raised when a recording cannot be analysed safely."""


@dataclass(frozen=True)
class WordDifference:
    kind: DifferenceKind
    reference: str
    heard: str


@dataclass(frozen=True)
class AcceptedAlternative:
    lesson_phrase: str
    accepted_phrase: str
    explanation: str


@dataclass(frozen=True)
class TranscriptComparison:
    reference: str
    transcript: str
    differences: tuple[WordDifference, ...]
    substitutions: int
    deletions: int
    insertions: int
    word_error_rate: float
    accepted_alternatives: tuple[AcceptedAlternative, ...] = ()

    @property
    def match_percent(self) -> int:
        """Return a friendly script-match percentage, clamped to 0-100."""
        return round(100 * max(0.0, 1.0 - self.word_error_rate))


@dataclass(frozen=True)
class PacingComparison:
    reference_duration: float
    learner_duration: float
    duration_ratio: float
    alignment_deviation: float
    similarity: float

    @property
    def label(self) -> str:
        if self.similarity >= 0.9:
            return "Close overall"
        if self.similarity >= 0.75:
            return "Some timing differences"
        return "Noticeably different"


@dataclass(frozen=True)
class SpeechFeedback:
    raw_transcript: str
    transcript: TranscriptComparison
    pacing: PacingComparison


def normalize_text(text: str) -> str:
    """Normalize case, punctuation, and spacing while preserving German letters."""
    lowered = text.lower()
    # Whisper often writes a spoken number as digits ("28") while an authored
    # beginner script spells it out ("achtundzwanzig"). Treat those spellings
    # as equivalent for the common 0-99 range instead of reporting a false error.
    lowered = re.sub(
        r"\b\d{1,2}\b",
        lambda match: _german_number_word(int(match.group())),
        lowered,
    )
    without_punctuation = re.sub(r"[^\w\s]", " ", lowered, flags=re.UNICODE)
    return re.sub(r"\s+", " ", without_punctuation).strip()


def _german_number_word(number: int) -> str:
    """Return the standard written German cardinal for an integer from 0 to 99."""
    small_numbers = {
        0: "null",
        1: "eins",
        2: "zwei",
        3: "drei",
        4: "vier",
        5: "fünf",
        6: "sechs",
        7: "sieben",
        8: "acht",
        9: "neun",
        10: "zehn",
        11: "elf",
        12: "zwölf",
        13: "dreizehn",
        14: "vierzehn",
        15: "fünfzehn",
        16: "sechzehn",
        17: "siebzehn",
        18: "achtzehn",
        19: "neunzehn",
    }
    if number in small_numbers:
        return small_numbers[number]
    tens = {
        20: "zwanzig",
        30: "dreißig",
        40: "vierzig",
        50: "fünfzig",
        60: "sechzig",
        70: "siebzig",
        80: "achtzig",
        90: "neunzig",
    }
    tens_value, ones = divmod(number, 10)
    tens_word = tens[tens_value * 10]
    if not ones:
        return tens_word
    ones_word = "ein" if ones == 1 else small_numbers[ones]
    return f"{ones_word}und{tens_word}"


def compare_transcript(
    reference: str,
    transcript: str,
    accepted_alternatives: tuple[AcceptedAlternative, ...] = (),
) -> TranscriptComparison:
    """Align two word sequences and return a minimal word-error comparison.

    This small dynamic-programming implementation keeps transcript comparison
    usable in unit tests without importing the optional audio dependencies.
    """
    normalized_reference = normalize_text(reference)
    normalized_transcript = normalize_text(transcript)
    used_alternatives: list[AcceptedAlternative] = []
    for alternative in sorted(
        accepted_alternatives,
        key=lambda item: len(normalize_text(item.accepted_phrase)),
        reverse=True,
    ):
        lesson_phrase = normalize_text(alternative.lesson_phrase)
        accepted_phrase = normalize_text(alternative.accepted_phrase)
        if not lesson_phrase or lesson_phrase not in normalized_reference:
            continue
        normalized_transcript, replacements = re.subn(
            rf"(?<!\w){re.escape(accepted_phrase)}(?!\w)",
            lesson_phrase,
            normalized_transcript,
        )
        if replacements:
            used_alternatives.append(alternative)
    reference_words = normalized_reference.split()
    transcript_words = normalized_transcript.split()
    if not reference_words:
        raise ValueError("Reference text must contain at least one word")

    rows = len(reference_words) + 1
    columns = len(transcript_words) + 1
    costs = [[0] * columns for _ in range(rows)]
    steps: list[list[str | None]] = [[None] * columns for _ in range(rows)]

    for row in range(1, rows):
        costs[row][0] = row
        steps[row][0] = "missing"
    for column in range(1, columns):
        costs[0][column] = column
        steps[0][column] = "extra"

    for row in range(1, rows):
        for column in range(1, columns):
            if reference_words[row - 1] == transcript_words[column - 1]:
                costs[row][column] = costs[row - 1][column - 1]
                steps[row][column] = "equal"
                continue

            candidates = (
                (costs[row - 1][column - 1] + 1, "different"),
                (costs[row - 1][column] + 1, "missing"),
                (costs[row][column - 1] + 1, "extra"),
            )
            # Candidate order intentionally prefers a substitution when costs tie.
            costs[row][column], steps[row][column] = min(
                candidates, key=lambda candidate: candidate[0]
            )

    operations: list[tuple[str, str, str]] = []
    row, column = len(reference_words), len(transcript_words)
    while row or column:
        step = steps[row][column]
        if step == "equal":
            operations.append(
                ("equal", reference_words[row - 1], transcript_words[column - 1])
            )
            row -= 1
            column -= 1
        elif step == "different":
            operations.append(
                ("different", reference_words[row - 1], transcript_words[column - 1])
            )
            row -= 1
            column -= 1
        elif step == "missing":
            operations.append(("missing", reference_words[row - 1], ""))
            row -= 1
        elif step == "extra":
            operations.append(("extra", "", transcript_words[column - 1]))
            column -= 1
        else:  # Defensive guard for an impossible incomplete alignment matrix.
            raise SpeechAnalysisError("Could not align the transcript with the lesson")
    operations.reverse()

    differences: list[WordDifference] = []
    previous_was_difference = False
    for kind, expected, heard in operations:
        if kind == "equal":
            previous_was_difference = False
            continue
        if previous_was_difference and differences[-1].kind == kind:
            previous = differences[-1]
            differences[-1] = WordDifference(
                kind=previous.kind,
                reference=" ".join(filter(None, (previous.reference, expected))),
                heard=" ".join(filter(None, (previous.heard, heard))),
            )
        else:
            differences.append(
                WordDifference(
                    kind=kind,  # type: ignore[arg-type]
                    reference=expected,
                    heard=heard,
                )
            )
        previous_was_difference = True

    substitutions = sum(kind == "different" for kind, _, _ in operations)
    deletions = sum(kind == "missing" for kind, _, _ in operations)
    insertions = sum(kind == "extra" for kind, _, _ in operations)
    word_error_rate = (substitutions + deletions + insertions) / len(reference_words)
    return TranscriptComparison(
        reference=reference,
        transcript=transcript.strip(),
        differences=tuple(differences),
        substitutions=substitutions,
        deletions=deletions,
        insertions=insertions,
        word_error_rate=word_error_rate,
        accepted_alternatives=tuple(used_alternatives),
    )


def create_whisper_model(
    model_name: str = "small", *, download_root: str | Path | None = None
) -> Any:
    """Create the optional local Whisper model used by the Streamlit cache."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as error:
        raise SpeechDependencyError(
            "Local speech feedback is not installed. Install requirements-speech.txt."
        ) from error

    options: dict[str, Any] = {"compute_type": "int8"}
    if download_root is not None:
        options["download_root"] = str(download_root)
    try:
        return WhisperModel(model_name, **options)
    except Exception as error:
        raise SpeechAnalysisError(f"The local speech model could not be loaded: {error}") from error


def transcribe_german(model: Any, recording_path: str | Path) -> str:
    """Transcribe one German recording without biasing it toward the script."""
    try:
        segments, _ = model.transcribe(
            str(recording_path),
            language="de",
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False,
        )
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
    except Exception as error:
        raise SpeechAnalysisError(f"The recording could not be transcribed: {error}") from error
    if not transcript:
        raise SpeechAnalysisError(
            "No speech was detected. Try again a little closer to the microphone."
        )
    return transcript


def _audio_features(path: str | Path) -> tuple[Any, float]:
    try:
        import librosa
        import numpy as np
    except ImportError as error:
        raise SpeechDependencyError(
            "Local pacing feedback is not installed. Install requirements-speech.txt."
        ) from error

    try:
        audio, sample_rate = librosa.load(path, sr=16_000, mono=True)
        audio, _ = librosa.effects.trim(audio, top_db=30)
    except Exception as error:
        raise SpeechAnalysisError(f"The recording could not be read: {error}") from error
    if len(audio) < sample_rate // 2 or not np.any(np.abs(audio) > 1e-5):
        raise SpeechAnalysisError("The recording is empty or too short to compare")

    features = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)[1:]
    features = (features - features.mean(axis=1, keepdims=True)) / (
        features.std(axis=1, keepdims=True) + 1e-8
    )
    return features, len(audio) / sample_rate


def compare_pacing(
    reference_audio_path: str | Path, learner_audio_path: str | Path
) -> PacingComparison:
    """Compare broad timing patterns after trimming outer silence.

    MFCC/DTW is useful for an approximate path comparison, but the returned
    value is intentionally treated as qualitative and not a pronunciation grade.
    """
    try:
        import librosa
        import numpy as np
    except ImportError as error:
        raise SpeechDependencyError(
            "Local pacing feedback is not installed. Install requirements-speech.txt."
        ) from error

    reference_features, reference_duration = _audio_features(reference_audio_path)
    learner_features, learner_duration = _audio_features(learner_audio_path)
    try:
        _, path = librosa.sequence.dtw(
            X=reference_features,
            Y=learner_features,
            metric="cosine",
        )
    except Exception as error:
        raise SpeechAnalysisError(f"Pacing could not be compared: {error}") from error

    path = np.asarray(path)
    reference_scale = max(reference_features.shape[1] - 1, 1)
    learner_scale = max(learner_features.shape[1] - 1, 1)
    deviation = float(
        np.mean(
            np.abs(path[:, 0] / reference_scale - path[:, 1] / learner_scale)
        )
    )
    duration_ratio = min(reference_duration, learner_duration) / max(
        reference_duration, learner_duration
    )
    path_similarity = max(0.0, 1.0 - 3.0 * deviation)
    similarity = 0.5 * path_similarity + 0.5 * duration_ratio
    return PacingComparison(
        reference_duration=reference_duration,
        learner_duration=learner_duration,
        duration_ratio=duration_ratio,
        alignment_deviation=deviation,
        similarity=similarity,
    )


def analyse_recording(
    *,
    reference_text: str,
    reference_audio_path: str | Path,
    learner_audio_path: str | Path,
    model: Any,
    accepted_alternatives: tuple[AcceptedAlternative, ...] = (),
) -> SpeechFeedback:
    """Produce cautious transcript and pacing feedback for one recording."""
    transcript = transcribe_german(model, learner_audio_path)
    return SpeechFeedback(
        raw_transcript=transcript,
        transcript=compare_transcript(
            reference_text,
            transcript,
            accepted_alternatives,
        ),
        pacing=compare_pacing(reference_audio_path, learner_audio_path),
    )


def revise_transcript(
    feedback: SpeechFeedback,
    *,
    reference_text: str,
    corrected_transcript: str,
    accepted_alternatives: tuple[AcceptedAlternative, ...] = (),
) -> SpeechFeedback:
    """Re-evaluate user-reviewed text without changing audio-derived pacing."""
    if not corrected_transcript.strip():
        raise SpeechAnalysisError("The reviewed transcript cannot be empty")
    return SpeechFeedback(
        raw_transcript=feedback.raw_transcript,
        transcript=compare_transcript(
            reference_text,
            corrected_transcript,
            accepted_alternatives,
        ),
        pacing=feedback.pacing,
    )
