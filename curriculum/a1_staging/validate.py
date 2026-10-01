"""Structural checks for the quarantined A1 draft corpus.

This module is intentionally independent of the production lesson loader.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LESSON_DIR = ROOT / "lessons"
EXPECTED_LESSONS = 48


def german_word_count(sentences: list[dict[str, str]]) -> int:
    text = " ".join(sentence["de"] for sentence in sentences)
    return len(re.findall(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)?|\d+", text))


def planned_limits(number: int) -> tuple[range, range]:
    if number <= 6:
        return range(3, 5), range(25, 43)
    if number <= 12:
        return range(3, 5), range(30, 46)
    if number <= 18:
        return range(4, 6), range(40, 59)
    if number <= 24:
        return range(4, 6), range(42, 59)
    if number <= 30:
        return range(4, 6), range(48, 63)
    if number <= 36:
        return range(4, 6), range(50, 66)
    if number <= 42:
        return range(5, 7), range(55, 71)
    return range(5, 7), range(60, 81)


def load_records() -> list[dict]:
    records: list[dict] = []
    for path in sorted(LESSON_DIR.glob("module_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"{path}: expected a JSON list")
        records.extend(payload)
    return records


def main() -> None:
    lessons = load_records()
    errors: list[str] = []

    if len(lessons) != EXPECTED_LESSONS:
        errors.append(f"expected {EXPECTED_LESSONS} lessons, found {len(lessons)}")

    for expected, lesson in enumerate(lessons, start=1):
        context = f"lesson {expected}"
        if lesson.get("blueprint_lesson") != expected:
            errors.append(f"{context}: wrong blueprint_lesson")
        if lesson.get("draft_id") != f"a1-draft-{expected:03d}":
            errors.append(f"{context}: wrong draft_id")
        if lesson.get("status") != "draft_unpublished":
            errors.append(f"{context}: status must be draft_unpublished")

        sentences = lesson.get("sentences")
        if not isinstance(sentences, list):
            errors.append(f"{context}: sentences must be a list")
            continue

        sentence_range, word_range = planned_limits(expected)
        if len(sentences) not in sentence_range:
            errors.append(
                f"{context}: {len(sentences)} sentences outside "
                f"{sentence_range.start}-{sentence_range.stop - 1}"
            )

        for sentence_number, sentence in enumerate(sentences, start=1):
            if not sentence.get("de", "").strip() or not sentence.get("en", "").strip():
                errors.append(
                    f"{context}, sentence {sentence_number}: missing German or English"
                )

        count = german_word_count(sentences)
        if count not in word_range:
            errors.append(
                f"{context}: {count} German words outside "
                f"{word_range.start}-{word_range.stop - 1}"
            )

        check = lesson.get("first_listen_check", {})
        if not check.get("prompt", "").strip() or not check.get("answer", "").strip():
            errors.append(f"{context}: incomplete first-listen check")

        forbidden = {"audio_path", "annotations", "breakdown_groups", "published"}
        present = forbidden.intersection(lesson)
        if present:
            errors.append(f"{context}: forbidden staging fields {sorted(present)}")

    if errors:
        raise SystemExit("\n".join(errors))

    print(f"Validated {len(lessons)} unpublished A1 passage drafts.")


if __name__ == "__main__":
    main()
