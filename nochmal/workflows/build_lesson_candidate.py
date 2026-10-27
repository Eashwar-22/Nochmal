"""Compile an authored lesson candidate into its exact app-ready artifact."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from nochmal.content.candidates import (  # noqa: E402
    artifact_json,
    artifact_path,
    candidate_directory,
    compile_candidate,
    load_candidate_source,
    preview_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson_id")
    arguments = parser.parse_args()

    source = load_candidate_source(arguments.lesson_id)
    lesson = compile_candidate(source)
    directory = candidate_directory(arguments.lesson_id)
    directory.mkdir(parents=True, exist_ok=True)
    artifact_path(arguments.lesson_id).write_text(
        artifact_json(source, lesson), encoding="utf-8"
    )
    (directory / "preview.md").write_text(
        preview_markdown(source, lesson), encoding="utf-8"
    )
    print(f"Built {artifact_path(arguments.lesson_id).relative_to(PROJECT_ROOT)}")
    print(f"Built {(directory / 'preview.md').relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
