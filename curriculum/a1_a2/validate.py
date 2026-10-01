from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LESSON_DIR = ROOT / "lessons"
WORD_RE = re.compile(r"\b[\wÄÖÜäöüß'-]+\b", re.UNICODE)
EXPECTED_FILES = ["001_020.json", "021_040.json", "041_060.json", "061_080.json"]
ALLOWED_FORMATS = {
    "narrative", "description", "dialogue", "message", "announcement", "instructions"
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def validate() -> list[str]:
    errors: list[str] = []
    source_ids = {item["id"] for item in load_json(ROOT / "sources.json")["sources"]}
    bands = load_json(ROOT / "sequence.json")["bands"]
    lessons: list[dict] = []

    for filename in EXPECTED_FILES:
        path = LESSON_DIR / filename
        if not path.is_file():
            errors.append(f"missing lesson file: {filename}")
            continue
        payload = load_json(path)
        if len(payload) != 20:
            errors.append(f"{filename}: expected 20 lessons, found {len(payload)}")
        lessons.extend(payload)

    if len(lessons) != 80:
        errors.append(f"expected 80 lessons, found {len(lessons)}")

    seen_ids: set[str] = set()
    introduced: set[str] = set()
    introduced_by: dict[str, int] = {}
    previous_sequence = 0

    for lesson in lessons:
        sequence = lesson.get("sequence")
        context = f"lesson {sequence!r}"
        if sequence != previous_sequence + 1:
            errors.append(f"{context}: sequence is not contiguous")
        previous_sequence = sequence if isinstance(sequence, int) else previous_sequence

        lesson_id = lesson.get("id", "")
        if lesson_id in seen_ids:
            errors.append(f"{context}: duplicate id {lesson_id!r}")
        seen_ids.add(lesson_id)

        expected_band = next(
            (band["name"] for band in bands if band["start"] <= sequence <= band["end"]),
            None,
        )
        if lesson.get("band") != expected_band:
            errors.append(f"{context}: expected band {expected_band}")
        if lesson.get("format") not in ALLOWED_FORMATS:
            errors.append(f"{context}: unsupported format {lesson.get('format')!r}")

        sentences = lesson.get("sentences", [])
        if not 3 <= len(sentences) <= 7:
            errors.append(f"{context}: expected 3-7 sentences")
        for index, sentence in enumerate(sentences, start=1):
            if not sentence.get("de", "").strip() or not sentence.get("en", "").strip():
                errors.append(f"{context}, sentence {index}: missing German or English")

        german = " ".join(sentence.get("de", "") for sentence in sentences)
        word_count = len(WORD_RE.findall(german))
        if not 18 <= word_count <= 115:
            errors.append(f"{context}: German passage has {word_count} words")

        new_targets = lesson.get("new_targets", [])
        if not 5 <= len(new_targets) <= 10:
            errors.append(f"{context}: expected 5-10 new targets")
        normalized_new = [target.casefold() for target in new_targets]
        if len(normalized_new) != len(set(normalized_new)):
            errors.append(f"{context}: duplicate new target")
        already_introduced = sorted(set(normalized_new) & introduced)
        if already_introduced:
            errors.append(
                f"{context}: target introduced more than once: "
                f"{', '.join(already_introduced)}"
            )

        recycled = [target.casefold() for target in lesson.get("recycled_targets", [])]
        unavailable = sorted(set(recycled) - introduced)
        if unavailable:
            errors.append(
                f"{context}: recycled before introduction: {', '.join(unavailable)}"
            )

        links = lesson.get("recycles_from", [])
        if any(not isinstance(link, int) or link >= sequence or link < 1 for link in links):
            errors.append(f"{context}: recycles_from must contain earlier sequences")

        unknown_sources = set(lesson.get("source_basis", [])) - source_ids
        if unknown_sources:
            errors.append(f"{context}: unknown sources {sorted(unknown_sources)}")
        expected_wordlist = "goethe-a1-wordlist" if lesson["band"].startswith("A1") else "goethe-a2-wordlist"
        if expected_wordlist not in lesson.get("source_basis", []):
            errors.append(f"{context}: missing {expected_wordlist} source basis")

        missing_origin_links = sorted(
            target
            for target in recycled
            if introduced_by.get(target) not in links
        )
        if missing_origin_links:
            errors.append(
                f"{context}: recycles_from omits target origins for "
                f"{', '.join(missing_origin_links)}"
            )

        check = lesson.get("comprehension", {})
        if not check.get("question_en", "").strip() or not check.get("answer_en", "").strip():
            errors.append(f"{context}: incomplete comprehension check")

        introduced.update(normalized_new)
        introduced_by.update({target: sequence for target in normalized_new})

    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        raise SystemExit("Curriculum validation failed:\n" + "\n".join(f"- {p}" for p in problems))
    print("Validated 80 ordered A1-A2 passage lessons.")
