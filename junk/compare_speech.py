"""
Compare a recitation (your recording) against an original German recording.

Setup:
    pip install faster-whisper jiwer librosa numpy

Usage:
    python compare_speech.py original.wav mine.wav
    python compare_speech.py original.wav mine.wav --model medium
    python compare_speech.py original.wav mine.wav --script script.txt   # use the real text as reference

What it measures:
  1. Words   - transcribes both recordings with Whisper (German), diffs the text (WER).
  2. Rhythm  - MFCC + dynamic time warping, so different timestamps don't matter;
               checks how much your pacing drifts from the original.
NOTE: Whisper tends to "autocorrect" unclear speech, so the word score is lenient
and it does NOT truly judge pronunciation/accent.
"""

import argparse
import re

import jiwer
import librosa
import numpy as np
from faster_whisper import WhisperModel


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)  # drop punctuation, keep umlauts/ß
    return re.sub(r"\s+", " ", text).strip()


def transcribe(model: WhisperModel, path: str) -> str:
    segments, _ = model.transcribe(
        path,
        language="de",
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    return " ".join(s.text.strip() for s in segments)


def word_score(reference: str, hypothesis: str):
    ref, hyp = normalize(reference), normalize(hypothesis)
    out = jiwer.process_words(ref, hyp)
    ref_words, hyp_words = ref.split(), hyp.split()

    print("\n--- Word differences (reference -> yours) ---")
    any_diff = False
    for chunk in out.alignments[0]:
        if chunk.type == "equal":
            continue
        any_diff = True
        r = " ".join(ref_words[chunk.ref_start_idx:chunk.ref_end_idx]) or "-"
        h = " ".join(hyp_words[chunk.hyp_start_idx:chunk.hyp_end_idx]) or "-"
        label = {"substitute": "WRONG  ", "delete": "MISSED ", "insert": "EXTRA  "}[chunk.type]
        print(f"{label} {r}  ->  {h}")
    if not any_diff:
        print("No differences.")

    print(
        f"\nWER: {out.wer:.2%}  (substitutions={out.substitutions}, "
        f"missed={out.deletions}, extra={out.insertions})"
    )
    return max(0.0, 1.0 - out.wer)


def load_features(path: str):
    y, sr = librosa.load(path, sr=16000, mono=True)
    y, _ = librosa.effects.trim(y, top_db=30)  # cut leading/trailing silence
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)[1:]  # drop energy coeff
    # per-recording mean/variance normalization reduces speaker/mic differences
    mfcc = (mfcc - mfcc.mean(axis=1, keepdims=True)) / (mfcc.std(axis=1, keepdims=True) + 1e-8)
    return mfcc, len(y) / sr


def rhythm_score(orig_path: str, mine_path: str):
    a, dur_a = load_features(orig_path)
    b, dur_b = load_features(mine_path)

    _, wp = librosa.sequence.dtw(X=a, Y=b, metric="cosine")
    wp = np.array(wp)  # (frame_in_a, frame_in_b) pairs

    # How far the alignment path strays from a straight diagonal (0 = same pacing)
    deviation = np.mean(np.abs(wp[:, 0] / a.shape[1] - wp[:, 1] / b.shape[1]))
    duration_ratio = min(dur_a, dur_b) / max(dur_a, dur_b)

    # Rough mapping to 0-1; tweak the constant (3.0) to taste after testing
    path_score = max(0.0, 1.0 - 3.0 * deviation)
    score = 0.5 * path_score + 0.5 * duration_ratio

    print("\n--- Rhythm / pacing ---")
    print(f"Original length: {dur_a:.1f}s | Yours: {dur_b:.1f}s (ratio {duration_ratio:.2f})")
    print(f"Alignment deviation: {deviation:.3f} -> path score {path_score:.2f}")
    return score


def main():
    p = argparse.ArgumentParser()
    p.add_argument("original")
    p.add_argument("mine")
    p.add_argument("--model", default="small", help="tiny/base/small/medium/large-v3")
    p.add_argument("--script", help="optional text file with the true script")
    args = p.parse_args()

    model = WhisperModel(args.model, compute_type="int8")  # CPU-friendly

    if args.script:
        with open(args.script, encoding="utf-8") as f:
            reference = f.read()
    else:
        reference = transcribe(model, args.original)
    mine = transcribe(model, args.mine)

    print("Reference text:", reference)
    print("Your text:     ", mine)

    w = word_score(reference, mine)
    r = rhythm_score(args.original, args.mine)

    final = 10 * (0.7 * w + 0.3 * r)
    print("\n=== Scores ===")
    print(f"Words:  {10 * w:.2f}/10")
    print(f"Rhythm: {10 * r:.2f}/10")
    print(f"Overall (70% words, 30% rhythm): {final:.2f}/10")


if __name__ == "__main__":
    main()