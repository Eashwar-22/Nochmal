"""Filesystem locations shared by the app, scripts, and tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_DIR = PROJECT_ROOT / "data"
