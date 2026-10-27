"""Share storage for byte-identical staged, candidate, published, and mobile clips.

All lesson paths stay available for previews and release validation. Published
clips are the canonical copy; audio writers replace files atomically so a later
regeneration cannot change a published clip through a shared inode.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from nochmal.content.course_paths import (
    candidate_audio_root,
    discovered_levels,
    published_audio_root,
    published_root,
    staged_audio_root,
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_pair(canonical: Path, duplicate: Path, *, apply: bool) -> int:
    """Link a verified duplicate to its canonical clip; return saved bytes."""
    if not canonical.is_file() or not duplicate.is_file():
        return 0
    if canonical.stat().st_ino == duplicate.stat().st_ino and canonical.stat().st_dev == duplicate.stat().st_dev:
        return 0
    if canonical.stat().st_dev != duplicate.stat().st_dev or digest(canonical) != digest(duplicate):
        return 0
    saved = duplicate.stat().st_size
    if apply:
        with tempfile.TemporaryDirectory(prefix="nochmal-link-", dir=duplicate.parent) as temporary:
            link = Path(temporary) / duplicate.name
            os.link(canonical, link)
            os.replace(link, duplicate)
    return saved


def compact_lesson(lesson_id: str, *, apply: bool) -> tuple[int, int]:
    catalog = json.loads((published_root(lesson_id) / "publication.json").read_text(encoding="utf-8"))
    if lesson_id not in catalog["published_lesson_ids"]:
        raise ValueError(f"{lesson_id} is not published")
    published = published_audio_root(lesson_id) / lesson_id
    manifest = json.loads((published / "manifest.json").read_text(encoding="utf-8"))
    names = [*manifest["sentence_files"], manifest["paragraph_file"]]
    candidate = candidate_audio_root(lesson_id) / lesson_id
    staged = staged_audio_root(manifest["draft_id"]) / manifest["draft_id"]
    mobile = PROJECT_ROOT / "web" / "dist" / "audio" / lesson_id
    count = saved = 0
    for name in names:
        canonical = published / name
        expected = manifest["paragraph_sha256"] if name == manifest["paragraph_file"] else manifest["sentence_sha256"][name]
        if not canonical.is_file() or digest(canonical) != expected:
            raise ValueError(f"Published audio failed its manifest: {canonical}")
        for duplicate in (candidate / name, staged / name, mobile / name):
            bytes_saved = compact_pair(canonical, duplicate, apply=apply)
            if bytes_saved:
                count += 1
                saved += bytes_saved
    return count, saved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson_ids", nargs="*", help="Published lesson IDs; default is all discovered published lessons")
    parser.add_argument("--apply", action="store_true", help="Replace verified duplicates with hard links")
    args = parser.parse_args()
    ids = args.lesson_ids
    if not ids:
        ids = []
        for level in discovered_levels():
            manifest = PROJECT_ROOT / "curriculum" / f"{level}_published" / "publication.json"
            if manifest.is_file():
                ids.extend(json.loads(manifest.read_text(encoding="utf-8"))["published_lesson_ids"])
    count = saved = 0
    for lesson_id in ids:
        lesson_count, lesson_saved = compact_lesson(lesson_id, apply=args.apply)
        count += lesson_count
        saved += lesson_saved
    action = "Compacted" if args.apply else "Could compact"
    print(f"{action} {count} duplicate clips ({saved / 1024 / 1024:.1f} MiB)")


if __name__ == "__main__":
    main()
