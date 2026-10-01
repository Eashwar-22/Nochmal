from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
WORD_RE = re.compile(r"[a-zäöüß]+")
IGNORED_WORDS = {
    "auf",
    "bescheid",
    "das",
    "der",
    "die",
    "geld",
    "haben",
    "im",
    "nehmen",
    "rad",
    "recht",
    "sagen",
    "sein",
    "sich",
}


def pdf_letters(path: Path) -> str:
    text = " ".join((page.extract_text() or "") for page in PdfReader(path).pages)
    return re.sub(r"[^a-zäöüß]+", "", text.casefold())


def possible_stem(word: str) -> str:
    if word.endswith("en") and len(word) > 6:
        return word[:-2]
    if word.endswith("n") and len(word) > 6:
        return word[:-1]
    if word.endswith("er") and len(word) > 6:
        return word[:-2]
    return word


def target_is_attested(target: str, wordlist: str) -> bool:
    words = [
        word
        for word in WORD_RE.findall(target.casefold())
        if word not in IGNORED_WORDS
    ]
    return all(
        word in wordlist
        or (len(possible_stem(word)) >= 5 and possible_stem(word) in wordlist)
        for word in words
    )


def load_lessons() -> list[dict]:
    lessons: list[dict] = []
    for path in sorted((ROOT / "lessons").glob("*.json")):
        lessons.extend(json.loads(path.read_text(encoding="utf-8")))
    return lessons


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check deliberate lesson targets against official Goethe PDFs."
    )
    parser.add_argument("--a1-pdf", required=True, type=Path)
    parser.add_argument("--a2-pdf", required=True, type=Path)
    args = parser.parse_args()

    wordlists = {"A1": pdf_letters(args.a1_pdf), "A2": pdf_letters(args.a2_pdf)}
    unmatched: list[str] = []
    checked = 0

    for lesson in load_lessons():
        level = "A1" if lesson["band"].startswith("A1") else "A2"
        for target in lesson["new_targets"]:
            checked += 1
            if not target_is_attested(target, wordlists[level]):
                unmatched.append(
                    f"lesson {lesson['sequence']} ({level}): {target}"
                )

    if unmatched:
        raise SystemExit(
            "Official wordlist audit failed:\n"
            + "\n".join(f"- {item}" for item in unmatched)
        )
    print(f"Matched {checked}/{checked} focus targets to the official wordlists.")


if __name__ == "__main__":
    main()
