"""Activate an already-compiled candidate as a local app preview."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from nochmal.content.candidates import (  # noqa: E402
    ACTIVE_PREVIEWS_ROOT,
    active_preview_path,
    artifact_path,
    load_candidate_artifact,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Push a prebuilt lesson into the local app preview. No AI is called."
    )
    parser.add_argument("lesson_id")
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove this lesson from the local app preview.",
    )
    arguments = parser.parse_args()
    destination = active_preview_path(arguments.lesson_id)

    if arguments.remove:
        if destination.exists():
            destination.unlink()
            print(f"Removed local preview {arguments.lesson_id}")
        else:
            print(f"Local preview {arguments.lesson_id} was not active")
        return

    load_candidate_artifact(arguments.lesson_id)
    ACTIVE_PREVIEWS_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(artifact_path(arguments.lesson_id), destination)
    print(f"Pushed {arguments.lesson_id} into the local app preview")
    print("Restart or refresh Streamlit to see it. Production publication is unchanged.")


if __name__ == "__main__":
    main()
