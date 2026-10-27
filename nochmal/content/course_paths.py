"""Level-neutral curriculum locations and lesson identifiers.

Adding a level requires curriculum directories such as ``b1_course`` and
``b1_published``. Workflow code discovers those directories; it does not need
an A1/A2/B1 branch.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from nochmal.paths import PROJECT_ROOT


LEVEL_PATTERN = re.compile(r"[a-z]+\d+", flags=re.IGNORECASE)
IDENTIFIER_PATTERN = re.compile(
    r"(?P<level>[a-z]+\d+)-(?P<kind>course|draft)-(?P<number>\d{3})$",
    flags=re.IGNORECASE,
)


def course_level(identifier: str) -> str:
    """Return the normalized CEFR-style level prefix from a lesson ID."""

    match = IDENTIFIER_PATTERN.fullmatch(identifier)
    if match is None:
        raise ValueError(
            "Expected a lesson ID such as a2-course-013 or b1-draft-001; "
            f"received {identifier!r}"
        )
    return match.group("level").lower()


def course_number(identifier: str) -> int:
    match = IDENTIFIER_PATTERN.fullmatch(identifier)
    if match is None:
        course_level(identifier)  # Raise the same helpful validation error.
        raise AssertionError("unreachable")
    return int(match.group("number"))


def course_identifier(level: str, number: int) -> str:
    normalized = normalize_level(level)
    if number < 1 or number > 999:
        raise ValueError("Lesson numbers must be between 001 and 999")
    return f"{normalized}-course-{number:03d}"


def normalize_level(level: str) -> str:
    normalized = level.lower()
    if LEVEL_PATTERN.fullmatch(normalized) is None:
        raise ValueError(f"Invalid course level {level!r}")
    return normalized


def curriculum_root() -> Path:
    return PROJECT_ROOT / "curriculum"


def candidate_root(level_or_identifier: str) -> Path:
    level = _level(level_or_identifier)
    return curriculum_root() / f"{level}_candidates"


def authored_root(level_or_identifier: str) -> Path:
    """Return the modern author-owned course directory for a level."""

    level = _level(level_or_identifier)
    return curriculum_root() / f"{level}_course"


def published_root(identifier: str) -> Path:
    return curriculum_root() / f"{course_level(identifier)}_published"


def blueprint_path(level_or_identifier: str) -> Path:
    level = _level(level_or_identifier)
    return curriculum_root() / f"{level}_blueprint.md"


def published_audio_root(identifier: str) -> Path:
    return PROJECT_ROOT / "assets" / "audio" / f"{course_level(identifier)}_published"


def staged_audio_root(identifier: str) -> Path:
    return PROJECT_ROOT / "assets" / "audio" / f"{course_level(identifier)}_staging"


def source_record_for_draft(draft_id: str) -> dict[str, object]:
    """Find an author-owned source record by its draft ID for any level.

    Modern courses use ``source_draft_id`` under ``<level>_course``. The
    older staging layout uses ``draft_id``. Reading both keeps existing audio
    assets usable while new levels need only the modern course layout.
    """

    level = course_level(draft_id)
    roots = (
        authored_root(level) / "lessons",
        curriculum_root() / f"{level}_staging" / "lessons",
    )
    matches: list[dict[str, object]] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            records = payload if isinstance(payload, list) else [payload]
            for record in records:
                if isinstance(record, dict) and record.get("source_draft_id", record.get("draft_id")) == draft_id:
                    matches.append(record)
    if len(matches) != 1:
        raise ValueError(f"Expected one source record for {draft_id!r}; found {len(matches)}")
    return matches[0]


def candidate_audio_root(identifier: str) -> Path:
    return PROJECT_ROOT / "assets" / "audio" / f"{course_level(identifier)}_candidates"


def discovered_levels() -> tuple[str, ...]:
    """Discover levels from curriculum folders, in CEFR order when possible."""

    levels: set[str] = set()
    for path in curriculum_root().glob("*_*"):
        if not path.is_dir():
            continue
        level, separator, role = path.name.rpartition("_")
        if separator and role in {"candidates", "course", "published", "staging"}:
            if LEVEL_PATTERN.fullmatch(level):
                levels.add(level.lower())
    return tuple(sorted(levels, key=level_sort_key))


def level_sort_key(level: str) -> tuple[str, int, str]:
    """Sort a1, a2, b1, b2 … without a fixed list of supported levels."""

    match = re.fullmatch(r"([a-z]+)(\d+)", normalize_level(level))
    if match is None:
        raise ValueError(f"Invalid course level {level!r}")
    return (match.group(1), int(match.group(2)), level)


def _level(level_or_identifier: str) -> str:
    return course_level(level_or_identifier) if "-" in level_or_identifier else normalize_level(level_or_identifier)
