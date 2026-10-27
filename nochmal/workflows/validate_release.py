"""Validate one production lesson against the complete publication gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from nochmal.validation.release import release_result  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson_id")
    arguments = parser.parse_args()
    result = release_result(arguments.lesson_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["verdict"] == "pass" else 1)


if __name__ == "__main__":
    main()
