"""The mobile export must preserve the typed lesson and release boundary."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from nochmal.workflows import mobile_lesson


class MobileLessonTests(unittest.TestCase):
    def test_installed_lessons_match_their_published_levels(self) -> None:
        dist = mobile_lesson.DIST
        entries = json.loads((dist / "lessons.json").read_text(encoding="utf-8"))["lessons"]
        self.assertEqual(len(entries), len({entry["id"] for entry in entries}))
        levels = {"A1.1": 0, "A1.2": 0, "A2.1": 0, "A2.2": 0}
        for entry in entries:
            lesson = json.loads((dist / entry["dataFile"]).read_text(encoding="utf-8"))["lesson"]
            self.assertEqual(entry["id"], lesson["id"])
            self.assertEqual(entry["level"], lesson["level"])
            levels[entry["level"]] += 1
        self.assertEqual(29, levels["A1.1"])
        self.assertEqual(18, levels["A1.2"])
        published_a2 = json.loads((mobile_lesson.ROOT / "curriculum/a2_published/publication.json").read_text(encoding="utf-8"))["published_lesson_ids"]
        self.assertEqual(set(published_a2), {entry["id"] for entry in entries if entry["id"].startswith("a2-course-")})
        self.assertEqual(len(published_a2), levels["A2.1"] + levels["A2.2"])

    def test_candidate_preview_stays_out_of_published_catalog(self) -> None:
        original = mobile_lesson.CATALOG.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(mobile_lesson, "PREPARED", Path(directory)):
                mobile_lesson.prepare_candidate("a2-course-001")
                package = Path(directory) / "a2-course-001"
                payload = json.loads((package / "lesson-data.json").read_text(encoding="utf-8"))
                self.assertEqual("a2-course-001", payload["lesson"]["id"])
                self.assertTrue((package / "audio" / "paragraph.wav").is_file())
                stale = package / "audio" / "old-sentence.wav"
                stale.write_bytes(b"obsolete")
                mobile_lesson.prepare_candidate("a2-course-001")
                self.assertFalse(stale.exists())
        self.assertEqual(original, mobile_lesson.CATALOG.read_bytes())

    def test_export_has_complete_shared_references(self) -> None:
        source, _audio, lesson = mobile_lesson.checked_lesson("a1-course-004")
        payload = json.loads(mobile_lesson.payload_for(lesson, source))
        self.assertEqual("a1-course-004", payload["lesson"]["id"])
        self.assertEqual(lesson.title, payload["lesson"]["title"])
        self.assertIn("nominative", payload["tag_descriptions"])
        inflections = [
            help_card
            for sentence in payload["lesson"]["sentences"]
            for group in sentence["breakdown_groups"]
            for item in group["items"]
            for help_card in item["inflection_help"]
        ]
        self.assertTrue(inflections)
        for help_card in inflections:
            self.assertEqual(
                {"nominative", "accusative", "dative", "genitive"},
                set(help_card["reference_table"]),
            )
            self.assertEqual(
                len(help_card["reference_columns"]),
                len(help_card["reference_table"]["nominative"]),
            )
            self.assertGreaterEqual(help_card["selected_column"], 0)

    def test_a2_uses_the_a2_published_lesson_collection(self) -> None:
        with patch.object(mobile_lesson, "lesson_files", return_value=(
            mobile_lesson.ROOT / "curriculum/a2_published/lessons/049.json",
            mobile_lesson.ROOT / "assets/audio/a2_published/a2-course-001",
        )), patch.object(mobile_lesson, "release_result", return_value={
            "verdict": "pass", "errors": []
        }):
            _source, _audio, lesson = mobile_lesson.checked_lesson("a2-course-001")
        self.assertEqual("a2-course-001", lesson.id)

    def test_install_verifies_copy_and_removes_prepared_package(self) -> None:
        lesson_id = "a2-course-013"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prepared = root / "prepared"
            dist = root / "dist"
            audio = root / "published-audio"
            source = root / "source.json"
            catalog = dist / "lessons.json"
            package = prepared / lesson_id
            (package / "audio").mkdir(parents=True)
            audio.mkdir()
            dist.mkdir()
            source.write_text("source", encoding="utf-8")
            (audio / "manifest.json").write_text('{"paragraph_file":"paragraph.wav"}', encoding="utf-8")
            (audio / "paragraph.wav").write_bytes(b"clip")
            (package / "lesson-data.json").write_bytes(b"payload")
            (package / "audio" / "paragraph.wav").write_bytes(b"clip")
            catalog.write_text('{"lessons":[]}', encoding="utf-8")
            with (
                patch.object(mobile_lesson, "PREPARED", prepared),
                patch.object(mobile_lesson, "DIST", dist),
                patch.object(mobile_lesson, "CATALOG", catalog),
                patch.object(mobile_lesson, "checked_lesson", return_value=(source, audio, SimpleNamespace(level="A2.1"))),
                patch.object(mobile_lesson, "payload_for", return_value=b"payload"),
                patch.object(mobile_lesson, "audio_names", return_value=["paragraph.wav"]),
            ):
                mobile_lesson.install(lesson_id)
            self.assertFalse(package.exists())
            self.assertEqual(b"payload", (dist / "lesson-data" / f"{lesson_id}.json").read_bytes())
            self.assertEqual(b"clip", (dist / "audio" / lesson_id / "paragraph.wav").read_bytes())
            self.assertEqual(lesson_id, json.loads(catalog.read_text(encoding="utf-8"))["lessons"][0]["id"])
            self.assertEqual("A2.1", json.loads(catalog.read_text(encoding="utf-8"))["lessons"][0]["level"])


if __name__ == "__main__":
    unittest.main()
